"""typewrappers -- wrapper classes for AE type and enumeration codes
(C) 2005-2008 HAS
"""
class AETypeBase(object):
	def __init__(self, code):
		if not isinstance(code, basestring):
			raise TypeError("invalid code (not a str object): %r" % code)
		elif len(code) != 4:
			raise ValueError("invalid code (not four bytes long): %r" % code)
		self._code = code
	code = property(lambda self: self._code)
	def __hash__(self):
		return hash(self._code)
	def __eq__(self, val):
		return val.__class__ == self.__class__ and val.code == self._code
	def __ne__(self, val):
		return not self == val
	def __repr__(self):
		s = ""
		for c in self._code:
			if 33 < ord(c) < 127 and c != "'":
				s += c
			else:
				s += "\\x%2.2x" % ord(c)
		return "aem.%s('%s')" % (self.__class__.__name__, s)
class AEType(AETypeBase):
	"""An AE type."""
class AEEnum(AETypeBase):
	"""An AE enumeration."""
class AEProp(AETypeBase):
	"""An AE property code."""
class AEKey(AETypeBase):
	"""An AE keyword."""