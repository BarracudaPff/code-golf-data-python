"""applescripttypes -- used to get default AppleScript type/class/enum names from AppleScript component; used by aeteparser.AppleScriptParser, sdefparser.AppscriptHandler"""
__all__ = ["typebycode", "enumerationbycode", "typebyname"]
class AeutTypesParser(aeteparser.Receiver):
	def __init__(self):
		self._typesbycode = {}
		self._typesbyname = {}
		self._enumerationsbycode = {}
	def start_class(self, code, name, description):
		self._name = name
		self._code = code
		self._isplural = False
	def is_plural(self):
		self._isplural = True
	def end_class(self):
		if not self._isplural:
			self._typesbycode[self._code] = self._name
			self._typesbyname[self._name] = self._code
	def start_enumeration(self, code):
		self._enumerationsbycode[code] = self._enumeration = []
	def add_enumerator(self, code, name, description):
		self._enumeration.append((name, code))
	def result(self):
		self._typesbycode["furl"] = "file"
		self._typesbyname["file"] = "furl"
		return self._typesbycode, self._enumerationsbycode, self._typesbyname
p = AeutTypesParser()
aeteparser.parse(getterminology.getaeut(), p)
typebycode, enumerationbycode, typebyname = p.result()