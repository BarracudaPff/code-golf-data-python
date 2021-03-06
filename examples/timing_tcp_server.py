"""
A variant of simple_tcp_server.py that measures the time it takes to
send N messages for a range of N.  (This was O(N**2) in a previous
version of asyncio.)
Note that running this example starts both the TCP server and client
in the same process.  It listens on port 1234 on 127.0.0.1, so it will
fail if this port is currently in use.
"""
import sys
import time
import random
import asyncio
import asyncio.streams
class MyServer:
	"""
    This is just an example of how a TCP server might be potentially
    structured.  This class has basically 3 methods: start the server,
    handle a client, and stop the server.
    Note that you don't have to follow this structure, it is really
    just an example or possible starting point.
    """
	def __init__(self):
		self.server = None
		self.clients = {}
	def _accept_client(self, client_reader, client_writer):
		"""
        This method accepts a new client connection and creates a Task
        to handle this client.  self.clients is updated to keep track
        of the new client.
        """
		task = asyncio.Task(self._handle_client(client_reader, client_writer))
		self.clients[task] = (client_reader, client_writer)
		def client_done(task):
			print("client task done:", task, file=sys.stderr)
			del self.clients[task]
		task.add_done_callback(client_done)
	@asyncio.coroutine
	def _handle_client(self, client_reader, client_writer):
		"""
        This method actually does the work to handle the requests for
        a specific client.  The protocol is line oriented, so there is
        a main loop that reads a line with a request and then sends
        out one or more lines back to the client with the result.
        """
		while True:
			data = (yield from client_reader.readline()).decode("utf-8")
			if not data:
				break
			cmd, *args = data.rstrip().split(" ")
			if cmd == "add":
				arg1 = float(args[0])
				arg2 = float(args[1])
				retval = arg1 + arg2
				client_writer.write("{!r}\n".format(retval).encode("utf-8"))
			elif cmd == "repeat":
				times = int(args[0])
				msg = args[1]
				client_writer.write("begin\n".encode("utf-8"))
				for idx in range(times):
					client_writer.write("{}. {}\n".format(idx + 1, msg + "x" * random.randint(10, 50)).encode("utf-8"))
				client_writer.write("end\n".encode("utf-8"))
			else:
				print("Bad command {!r}".format(data), file=sys.stderr)
			yield from client_writer.drain()
	def start(self, loop):
		"""
        Starts the TCP server, so that it listens on port 1234.
        For each client that connects, the accept_client method gets
        called.  This method runs the loop until the server sockets
        are ready to accept connections.
        """
		self.server = loop.run_until_complete(asyncio.streams.start_server(self._accept_client, "127.0.0.1", 12345, loop=loop))
	def stop(self, loop):
		"""
        Stops the TCP server, i.e. closes the listening socket(s).
        This method runs the loop until the server sockets are closed.
        """
		if self.server is not None:
			self.server.close()
			loop.run_until_complete(self.server.wait_closed())
			self.server = None
def main():
	loop = asyncio.get_event_loop()
	server = MyServer()
	server.start(loop)
	@asyncio.coroutine
	def client():
		reader, writer = yield from asyncio.streams.open_connection("127.0.0.1", 12345, loop=loop)
		def send(msg):
			print("> " + msg)
			writer.write((msg + "\n").encode("utf-8"))
		def recv():
			msgback = (yield from reader.readline()).decode("utf-8").rstrip()
			print("< " + msgback)
			return msgback
		send("add 1 2")
		msg = yield from recv()
		Ns = list(range(100, 100000, 10000))
		times = []
		for N in Ns:
			t0 = time.time()
			send("repeat {} hello world ".format(N))
			msg = yield from recv()
			assert msg == "begin"
			while True:
				msg = (yield from reader.readline()).decode("utf-8").rstrip()
				if msg == "end":
					break
			t1 = time.time()
			dt = t1 - t0
			print("Time taken: {:.3f} seconds ({:.6f} per repetition)".format(dt, dt / N))
			times.append(dt)
		writer.close()
		yield from asyncio.sleep(0.5)
	try:
		loop.run_until_complete(client())
		server.stop(loop)
	finally:
		loop.close()
if __name__ == "__main__":
	main()