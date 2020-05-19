"Core exceptions raised by the Redis client"
class RedisError(Exception):
	pass
if not hasattr(RedisError, "__unicode__"):
	def __unicode__(self):
		if isinstance(self.args[0], unicode):
			return self.args[0]
		return unicode(self.args[0])
	RedisError.__unicode__ = __unicode__
class AuthenticationError(RedisError):
	pass
class ConnectionError(RedisError):
	pass
class TimeoutError(RedisError):
	pass
class BusyLoadingError(ConnectionError):
	pass
class InvalidResponse(RedisError):
	pass
class ResponseError(RedisError):
	pass
class DataError(RedisError):
	pass
class PubSubError(RedisError):
	pass
class WatchError(RedisError):
	pass
class NoScriptError(ResponseError):
	pass
class ExecAbortError(ResponseError):
	pass
class ReadOnlyError(ResponseError):
	pass
class LockError(RedisError, ValueError):
	"Errors acquiring or releasing a lock"
	pass