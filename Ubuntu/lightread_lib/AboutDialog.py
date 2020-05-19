class AboutDialog(Gtk.AboutDialog):
	__gtype_name__ = "AboutDialog"
	def __new__(cls):
		"""Special static method that's automatically called by Python when
        constructing a new instance of this class.
        Returns a fully instantiated AboutDialog object.
        """
		builder = get_builder("AboutLightreadDialog")
		new_object = builder.get_object("about_lightread_dialog")
		new_object.finish_initializing(builder)
		return new_object
	def finish_initializing(self, builder):
		"""Called while initializing this instance in __new__
        finish_initalizing should be called after parsing the ui definition
        and creating a AboutDialog object with it in order
        to finish initializing the start of the new AboutLightreadDialog
        instance.
        Put your initialization code in here and leave __init__ undefined.
        """
		self.builder = builder
		self.ui = builder.get_ui(self)