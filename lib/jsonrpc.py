from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler
from base64 import b64decode
import time
from . import util
class RPCAuthCredentialsInvalid(Exception):
	def __str__(self):
		return "Authentication failed (bad credentials)"
class RPCAuthCredentialsMissing(Exception):
	def __str__(self):
		return "Authentication failed (missing credentials)"
class RPCAuthUnsupportedType(Exception):
	def __str__(self):
		return "Authentication failed (only basic auth is supported)"
class VerifyingJSONRPCServer(SimpleJSONRPCServer):
	def __init__(self, *args, rpc_user, rpc_password, **kargs):
		self.rpc_user = rpc_user
		self.rpc_password = rpc_password
		class VerifyingRequestHandler(SimpleJSONRPCRequestHandler):
			def parse_request(myself):
				if SimpleJSONRPCRequestHandler.parse_request(myself):
					try:
						self.authenticate(myself.headers)
						return True
					except (RPCAuthCredentialsInvalid, RPCAuthCredentialsMissing, RPCAuthUnsupportedType) as e:
						myself.send_error(401, str(e))
					except BaseException as e:
						import traceback, sys
						traceback.print_exc(file=sys.stderr)
						myself.send_error(500, str(e))
				return False
		SimpleJSONRPCServer.__init__(self, requestHandler=VerifyingRequestHandler, *args, **kargs)
	def authenticate(self, headers):
		if self.rpc_password == "":
			return
		auth_string = headers.get("Authorization", None)
		if auth_string is None:
			raise RPCAuthCredentialsMissing()
		(basic, _, encoded) = auth_string.partition(" ")
		if basic != "Basic":
			raise RPCAuthUnsupportedType()
		encoded = util.to_bytes(encoded, "utf8")
		credentials = util.to_string(b64decode(encoded), "utf8")
		(username, _, password) = credentials.partition(":")
		if not (util.constant_time_compare(username, self.rpc_user) and util.constant_time_compare(password, self.rpc_password)):
			time.sleep(0.050)
			raise RPCAuthCredentialsInvalid()