try:
	pass
except ImportError:
	sys.exit("install SimpleWebSocketServer")
request_queue = queue.Queue()
class ElectrumWebSocket(WebSocket):
	def handleMessage(self):
		assert self.data[0:3] == "id:"
		util.print_error("message received", self.data)
		request_id = self.data[3:]
		request_queue.put((self, request_id))
	def handleConnected(self):
		util.print_error("connected", self.address)
	def handleClose(self):
		util.print_error("closed", self.address)
class WsClientThread(util.DaemonThread):
	def __init__(self, config, network):
		util.DaemonThread.__init__(self)
		self.network = network
		self.config = config
		self.response_queue = queue.Queue()
		self.subscriptions = defaultdict(list)
	def make_request(self, request_id):
		rdir = self.config.get("requests_dir")
		n = os.path.join(rdir, "req", request_id[0], request_id[1], request_id, request_id + ".json")
		with open(n) as f:
			s = f.read()
		d = json.loads(s)
		addr = d.get("address")
		amount = d.get("amount")
		return addr, amount
	def reading_thread(self):
		while self.is_running():
			try:
				ws, request_id = request_queue.get()
			except queue.Empty:
				continue
			try:
				addr, amount = self.make_request(request_id)
			except:
				continue
			l = self.subscriptions.get(addr, [])
			l.append((ws, amount))
			self.subscriptions[addr] = l
			h = self.network.addr_to_scripthash(addr)
			self.network.send([("blockchain.scripthash.subscribe", [h])], self.response_queue.put)
	def run(self):
		threading.Thread(target=self.reading_thread).start()
		while self.is_running():
			try:
				r = self.response_queue.get(timeout=0.1)
			except queue.Empty:
				continue
			util.print_error("response", r)
			method = r.get("method")
			params = r.get("params")
			result = r.get("result")
			if result is None:
				continue
			if method == "blockchain.scripthash.subscribe":
				self.network.send([("blockchain.scripthash.get_balance", params)], self.response_queue.put)
			elif method == "blockchain.scripthash.get_balance":
				h = params[0]
				addr = self.network.h2addr.get(h, None)
				if addr is None:
					util.print_error("can't find address for scripthash: %s" % h)
				l = self.subscriptions.get(addr, [])
				for ws, amount in l:
					if not ws.closed:
						if sum(result.values()) >= amount:
							ws.sendMessage("paid")
class WebSocketServer(threading.Thread):
	def __init__(self, config, ns):
		threading.Thread.__init__(self)
		self.config = config
		self.net_server = ns
		self.daemon = True
	def run(self):
		t = WsClientThread(self.config, self.net_server)
		t.start()
		host = self.config.get("websocket_server")
		port = self.config.get("websocket_port", 9999)
		certfile = self.config.get("ssl_chain")
		keyfile = self.config.get("ssl_privkey")
		self.server = SimpleSSLWebSocketServer(host, port, ElectrumWebSocket, certfile, keyfile)
		self.server.serveforever()