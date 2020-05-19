"""aeteparser -- parse an application's aete, given an application path, file path(s) or aete string. Returns a Dictionary object model.
(C) 2006 HAS
"""
_expandedtypes = {"lr  ": ["list", "reco"], "ls  ": ["list", "TEXT"], "ns  ": ["nmbr", "TEXT"], "sf  ": ["alis", "TEXT"], "lrs ": ["list", "reco", "TEXT"], "nd  ": ["nmbr", "ldt "], "nds ": ["nmbr", "ldt ", "TEXT"]}
class _Parser(aeteparser.Receiver):
	def __init__(self, path=""):
		self._visibility = [kVisible]
		name = "/" in path and (path.split("/")[-1] or path.split("/")[-2]) or path
		self._stack = [Dictionary(self._visibility, name, path)]
		self._visible = True
		self._types = {}
		self._classes = []
		self._pluralclassnames = {}
		self._accessors = {kAE.formAbsolutePosition: Accessor(self._visibility, "index"), kAE.formName: Accessor(self._visibility, "name"), kAE.formUniqueID: Accessor(self._visibility, "id"), kAE.formRange: Accessor(self._visibility, "range"), kAE.formRelativePosition: Accessor(self._visibility, "relative"), kAE.formTest: Accessor(self._visibility, "test")}
	def asname(self, s):
		return s
	def _gettype(self, code):
		if not self._types.has_key(code):
			self._types[code] = Type(self._visibility, code=code)
		return self._types[code]
	def _end(self):
		n = self._stack.pop()
		self._stack[-1]._add_(n)
	def addtypes(self, type, islist, parent):
		for code in _expandedtypes.get(type, [type]):
			t = self._gettype(code=code)
			if islist:
				t = ListOfType(self._visibility, t)
			parent._add_(t)
	def start_suite(self, code, name, description):
		self._visible = code != "tpnm"
		self._stack.append(Suite(self._visibility, name, code, description, self._visible))
	def end_suite(self):
		self._visible = True
		self._end()
	def start_command(self, code, name, description, directarg, reply):
		self._kargs = []
		suitename = self._stack[-1].name
		self._stack.append(Command(self._visibility, self.asname(name), code, description, self._visible, suitename))
		description, type, isoptional, islist, isenum = directarg
		if type != "null":
			o = DirectParameter(self._visibility, description, self._visible, isoptional)
			self.addtypes(type, islist, o)
			self._stack[-1]._add_(o)
		description, type, isoptional, islist, isenum = reply
		if type != "null":
			o = Result(self._visibility, description)
			self.addtypes(type, islist, o)
			self._stack[-1]._add_(o)
	def add_labelledarg(self, code, name, description, type, isoptional, islist, isenum):
		o = Parameter(self._visibility, self.asname(name), code, description, self._visible, isoptional)
		self.addtypes(type, islist, o)
		self._stack[-1]._add_(o)
	end_command = _end
	def start_class(self, code, name, description):
		self._isPlural = False
		name = self.asname(name)
		suitename = self._stack[-1].name
		o = Class(self._visibility, name, code, description, self._visible, name, suitename, self._gettype(code))
		self._stack.append(o)
	def end_class(self):
		o = self._stack.pop()
		if self._isPlural:
			self._pluralclassnames[o.code] = o.name
		else:
			self._stack[-1]._add_(o)
			self._classes.append(o)
			t = self._gettype(o.code)
			t.name = o.name
			t._add_(o)
	def add_superclass(self, type):
		self._stack[-1]._add_(self._gettype(code=type))
	def is_plural(self):
		self._isPlural = True
	def add_property(self, code, name, description, type, islist, isenum, ismutable):
		o = Property(self._visibility, self.asname(name), code, description, self._visible, ismutable and "rw" or "r")
		self.addtypes(type, islist, o)
		self._stack[-1]._add_(o)
	def start_element(self, type):
		self._stack.append(Element(self._visibility, self._gettype(type), "", self._visible, "rw", self.elementnamesareplural))
	def add_supportedform(self, formcode):
		try:
			self._stack[-1]._add_(self._accessors[formcode])
		except KeyError:
			pass
	end_element = _end
	def start_enumeration(self, code):
		suitename = self._stack[-1].name
		o = Enumeration([kAll], "", code, "", self._visible, None, suitename)
		self._stack.append(o)
		t = self._gettype(code)
		t.name = code
		t._add_(o)
	def add_enumerator(self, code, name, description):
		self._stack[-1]._add_(Enumerator([kAll], self.asname(name), code, description, self._visible))
	end_enumeration = _end
	def result(self):
		for klass in self._classes:
			klass.pluralname = self._pluralclassnames.get(klass.code, klass.name)
		defs = self.typemodule()
		for type in self._types.values():
			if not type.name:
				if defs.typebycode.has_key(type.code):
					type.name = defs.typebycode[type.code]
				elif defs.enumerationbycode.has_key(type.code):
					type._add_(Enumeration(self._visibility, "", k, "", True, None))
					for name, code in defs.enumerationbycode[code]:
						type._add_(Enumerator(self._visibility, name, code, "", True))
		return self._stack[0]
class AppleScriptParser(_Parser):
	elementnamesareplural = False
	def typemodule(self):
		return applescripttypes
class AppscriptParser(_Parser):
	elementnamesareplural = True
	def typemodule(self):
		return appscripttypes
	def start_command(self, code, name, description, directarg, reply):
		if (name == "get" and code != "coregetd") or (name == "set" and code != "coresetd"):
			name += "_"
		_Parser.start_command(self, code, name, description, directarg, reply)
class PyAppscriptParser(AppscriptParser):
	asname = staticmethod(makeidentifier.getconverter("py-appscript"))
class RbAppscriptParser(AppscriptParser):
	asname = staticmethod(makeidentifier.getconverter("rb-appscript"))
_parsers = {"applescript": AppleScriptParser, "appscript": PyAppscriptParser, "py-appscript": PyAppscriptParser, "rb-appscript": RbAppscriptParser}
def parsedata(aetes, path="", style="appscript"):
	p = _parsers[style](path)
	aeteparser.parse(aetes, p)
	return p.result()
parsestring = parsedata
def parselang(code="ascr", style="appscript"):
	return parsedata(getterminology.getaeut(code), "", style)
def parsefile(paths, style="appscript"):
	if isinstance(paths, basestring):
		paths = [paths]
	aetes = []
	for path in paths:
		f = file(path)
		aetes.append(f.read())
		f.close()
	return parsedata(aetes, paths[0], style)
def parseapp(path, style="appscript"):
	return parsedata(getterminology.getaete(path), path, style)