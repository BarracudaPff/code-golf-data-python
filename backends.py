class BackendHandler(webapp2.RequestHandler):
	def get(self):
		pass
app = webapp2.WSGIApplication(routes=[(r"/_ah/.*", BackendHandler)])