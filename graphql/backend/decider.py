if False:
	pass
DEFAULT_TIMEOUT = 10
logger = logging.getLogger("graphql.errors")
class AsyncWorker(object):
	_terminator = object()
	def __init__(self, shutdown_timeout=DEFAULT_TIMEOUT):
		check_threads()
		self._queue = Queue(-1)
		self._lock = threading.Lock()
		self._thread = None
		self._thread_for_pid = None
		self.options = {"shutdown_timeout": shutdown_timeout}
		self.start()
	def is_alive(self):
		if self._thread_for_pid != os.getpid():
			return False
		return self._thread and self._thread.is_alive()
	def _ensure_thread(self):
		if self.is_alive():
			return
		self.start()
	def main_thread_terminated(self):
		with self._lock:
			if not self.is_alive():
				return
			self._queue.put_nowait(self._terminator)
			timeout = self.options["shutdown_timeout"]
			initial_timeout = min(0.1, timeout)
			if not self._timed_queue_join(initial_timeout):
				size = self._queue.qsize()
				print("GraphQL is attempting to retrieve %i pending documents" % size)
				print("Waiting up to %s seconds" % timeout)
				if os.name == "nt":
					print("Press Ctrl-Break to quit")
				else:
					print("Press Ctrl-C to quit")
				self._timed_queue_join(timeout - initial_timeout)
			self._thread = None
	def _timed_queue_join(self, timeout):
		"""
        implementation of Queue.join which takes a 'timeout' argument
        returns true on success, false on timeout
        """
		deadline = time() + timeout
		queue = self._queue
		queue.all_tasks_done.acquire()
		try:
			while queue.unfinished_tasks:
				delay = deadline - time()
				if delay <= 0:
					return False
				queue.all_tasks_done.wait(timeout=delay)
			return True
		finally:
			queue.all_tasks_done.release()
	def start(self):
		"""
        Starts the task thread.
        """
		self._lock.acquire()
		try:
			if not self.is_alive():
				self._thread = threading.Thread(target=self._target, name="graphql.AsyncWorker")
				self._thread.setDaemon(True)
				self._thread.start()
				self._thread_for_pid = os.getpid()
		finally:
			self._lock.release()
			atexit.register(self.main_thread_terminated)
	def stop(self, timeout=None):
		"""
        Stops the task thread. Synchronous!
        """
		with self._lock:
			if self._thread:
				self._queue.put_nowait(self._terminator)
				self._thread.join(timeout=timeout)
				self._thread = None
				self._thread_for_pid = None
	def queue(self, callback, *args, **kwargs):
		self._ensure_thread()
		self._queue.put_nowait((callback, args, kwargs))
	def _target(self):
		while True:
			record = self._queue.get()
			try:
				if record is self._terminator:
					break
				callback, args, kwargs = record
				try:
					callback(*args, **kwargs)
				except Exception:
					logger.error("Failed processing job", exc_info=True)
			finally:
				self._queue.task_done()
			sleep(0)
class GraphQLDeciderBackend(GraphQLCachedBackend):
	"""GraphQLDeciderBackend will offload the document generation to the
    main backend in a new thread, serving meanwhile the document from the fallback
    backend"""
	_worker = None
	fallback_backend = None
	def __init__(self, backend, fallback_backend=None, cache_map=None, use_consistent_hash=False, worker_class=AsyncWorker):
		if not backend:
			raise Exception("Need to provide backends to decide into.")
		if isinstance(backend, (list, tuple)):
			if fallback_backend:
				raise Exception("Can't set a fallback backend and backends as array")
			if len(backend) != 2:
				raise Exception("Only two backends are supported for now")
			backend, fallback_backend = backend[0], backend[1]
		else:
			if not fallback_backend:
				raise Exception("Need to provide a fallback backend")
		self.fallback_backend = fallback_backend
		self.worker_class = worker_class
		super(GraphQLDeciderBackend, self).__init__(backend, cache_map=cache_map, use_consistent_hash=use_consistent_hash)
	def queue_backend(self, key, schema, request_string):
		self.cache_map[key] = self.backend.document_from_string(schema, request_string)
	def get_worker(self):
		if self._worker is None or not self._worker.is_alive():
			self._worker = self.worker_class()
		return self._worker
	def document_from_string(self, schema, request_string):
		"""This method returns a GraphQLQuery (from cache if present)"""
		key = self.get_key_for_schema_and_document_string(schema, request_string)
		if key not in self.cache_map:
			self.cache_map[key] = self.fallback_backend.document_from_string(schema, request_string)
			self.get_worker().queue(self.queue_backend, key, schema, request_string)
		return self.cache_map[key]