from datetime import datetime
class NodeWeight:
	SPEED_RECORD_COUNT = 3
	SPEED_INIT_VALUE = 100 * 1024 ^ 2
	REQUEST_TIME_RECORD_COUNT = 3
	def __init__(self, nodeid):
		self.id: int = nodeid
		self.speed = [self.SPEED_INIT_VALUE] * self.SPEED_RECORD_COUNT
		self.timeout_count = 0
		self.error_response_count = 0
		now = datetime.utcnow().timestamp() * 1000
		self.request_time = [now] * self.REQUEST_TIME_RECORD_COUNT
	def append_new_speed(self, speed) -> None:
		self.speed.pop(-1)
		self.speed.insert(0, speed)
	def append_new_request_time(self) -> None:
		self.request_time.pop(-1)
		now = datetime.utcnow().timestamp() * 1000
		self.request_time.insert(0, now)
	def _avg_speed(self) -> float:
		return sum(self.speed) / self.SPEED_RECORD_COUNT
	def _avg_request_time(self) -> float:
		avg_request_time = 0
		now = datetime.utcnow().timestamp() * 1000
		for t in self.request_time:
			avg_request_time += now - t
		avg_request_time = avg_request_time / self.REQUEST_TIME_RECORD_COUNT
		return avg_request_time
	def weight(self):
		weight = self._avg_speed() + self._avg_request_time()
		if self.error_response_count:
			weight /= self.error_response_count + 1
		if self.timeout_count:
			weight /= self.timeout_count + 1
		return weight
	def __lt__(self, other):
		return self.weight() < other.weight()
	def __repr__(self):
		return f"{self.id} {self._avg_speed():.2f} {self._avg_request_time():.2f} w:{self.weight():.2f} r:{self.error_response_count} t:{self.timeout_count}"