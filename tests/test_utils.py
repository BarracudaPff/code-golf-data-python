"""
Created on 20.04.15
@author = mharder
"""
def test_api_from_host():
	host = "test_host"
	port = 1235
	end_point = "/"
	user = "test"
	scheme = False
	api = api_from_host(host, port, end_point, user, scheme)
	assert api.host == host
	assert api.port == port
	assert api.username == user