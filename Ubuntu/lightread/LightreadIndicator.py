class LightreadIndicator:
	def __init__(self, main_app_window):
		self.main_app = main_app_window
		self.is_visible = False
		self.indicators = {}
		self.desktop_file = "/usr/share/applications/extras-lightread.desktop"
		self.server = Indicate.Server.ref_default()
		self.server.set_type("message.mail")
		self.server.set_desktop_file(self.desktop_file)
		self.server.connect("server-display", self.display_main_app)
	def add_indicator(self, feed_id, feed_title, feed_count):
		if feed_id in self.indicators.keys():
			indicator = self.indicators[feed_id]
		else:
			indicator = Indicate.Indicator()
			indicator.set_property("subtype", "mail")
			indicator.set_property("name", feed_title)
			indicator.connect("user-display", self.display_feed, feed_id)
			self.indicators[feed_id] = indicator
			self.server.add_indicator(indicator)
		indicator.set_property("count", str(feed_count))
		indicator.set_property("draw-attention", "true")
		indicator.show()
	def remove_indicator(self, feed_id):
		if feed_id in self.indicators.keys():
			indicator = self.indicators[feed_id]
			self.server.remove_indicator(indicator)
	def display_main_app(self, indicator, signal):
		is_visible = self.main_app.get_property("visible")
		if is_visible:
			self.main_app.present()
		else:
			self.main_app.show()
	def display_feed(self, indicator, signal, feed_id):
		self.display_main_app(indicator, signal)
		self.main_app.select_feed(feed_id)
	def hide(self):
		self.server.hide()
		self.is_visible = False
	def show(self):
		self.server.show()
		self.is_visible = True