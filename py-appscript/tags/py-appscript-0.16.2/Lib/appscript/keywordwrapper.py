"""keywordwrapper -- generic wrapper for application-specific type and enum names.
(C) 2004 HAS"""
class Keyword:
	"""A class/property/enumerator/type name."""
	def __init__(self, name):
		self.AS_name = name
	def __repr__(self):
		return "k.%s" % self.AS_name
	def __hash__(self):
		return hash(self.AS_name)
	def __eq__(self, val):
		return val.__class__ == self.__class__ and val.AS_name == self.AS_name
	def __ne__(self, val):
		return not self.__eq__(val)
	def __nonzero__(self):
		return self.AS_name != "MissingValue"
	name = property(lambda self: self.AS_name)
class _KeywordShim:
	def __getattr__(self, name):
		return Keyword(name)
k = _KeywordShim()