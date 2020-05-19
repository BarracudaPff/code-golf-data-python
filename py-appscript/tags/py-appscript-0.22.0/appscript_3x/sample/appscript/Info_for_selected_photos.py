from appscript import *
def infoforselectedphotos():
	"""Get properties of currently selected photo(s) in iPhoto."""
	selection = app("iPhoto").selection.get()
	photos = []
	if selection[0].class_.get() == k.photo:
		for photo in selection:
			photos.append(photo.properties.get())
	else:
		raise RuntimeError("No photos selected.")
	return photos
from pprint import pprint
pprint(infoforselectedphotos())