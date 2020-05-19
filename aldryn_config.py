try:
	pass
except ImportError:
	pass
class Form(forms.BaseForm):
	def to_settings(self, data, settings):
		settings["ADDON_URLS"].append("djangocms_blog.taggit_urls")
		return settings