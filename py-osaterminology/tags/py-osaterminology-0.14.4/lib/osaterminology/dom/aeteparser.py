"""aeteparser -- parse an application's aete, given an application path, file path(s) or aete string. Returns a Dictionary object model.
(C) 2006 HAS
"""
from aem.ae import newdesc, getappterminology, getsysterminology
from aem import kae
from osadictionary import *
from osaterminology import makeidentifier
from osaterminology.sax import aeteparser
import applescripttypes, appscripttypes
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
		self._accessors = {kae.formAbsolutePosition: Accessor(self._visibility, "index"), kae.formName: Accessor(self._visibility, "name"), kae.formUniqueID: Accessor(self._visibility, "id"), kae.formRange: Accessor(self._visibility, "range"), kae.formRelativePosition: Accessor(self._visibility, "relative"), kae.formTest: Accessor(self._visibility, "test")}
	def asname(self, name, code):
		return name
	def ascommandname(self, name, code):
		return name
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
		self._stack.append(Command(self._visibility, self.ascommandname(name, code), code, description, self._visible, suitename))
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
		o = Parameter(self._visibility, self.asname(name, code), code, description, self._visible, isoptional)
		self.addtypes(type, islist, o)
		self._stack[-1]._add_(o)
	end_command = _end
	def start_class(self, code, name, description):
		self._isPlural = False
		name = self.asname(name, code)
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
		o = Property(self._visibility, self.asname(name, code), code, description, self._visible, ismutable and "rw" or "r")
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
		self._stack[-1]._add_(Enumerator([kAll], self.asname(name, code), code, description, self._visible))
	end_enumeration = _end
	def result(self):
		for klass in self._classes:
			klass.pluralname = self._pluralclassnames.get(klass.code, klass.name)
		for type in self._types.values():
			if not type.name:
				if self.typemodule.typebycode.has_key(type.code):
					type.name = self.typemodule.typebycode[type.code]
				elif self.typemodule.enumerationbycode.has_key(type.code):
					type._add_(Enumeration(self._visibility, "", k, "", True, None))
					for name, code in self.typemodule.enumerationbycode[code]:
						type._add_(Enumerator(self._visibility, name, code, "", True))
		return self._stack[0]
class AppleScriptParser(_Parser):
	elementnamesareplural = False
	typemodule = applescripttypes
class _AppscriptParser(_Parser):
	elementnamesareplural = True
	def ascommandname(self, name, code):
		name = self._asname(name)
		if self.typemodule.commandcodebyname.get(name, code) != code:
			name += "_"
		return name
	def asname(self, name, code):
		name = self._asname(name)
		if self.typemodule.typecodebyname.get(name, code) != code:
			name += "_"
		return name
class ObjCAppscriptParser(_AppscriptParser):
	_asname = staticmethod(makeidentifier.getconverter("objc-appscript"))
	typemodule = appscripttypes.typetables("objc-appscript")
class PyAppscriptParser(_AppscriptParser):
	_asname = staticmethod(makeidentifier.getconverter("py-appscript"))
	typemodule = appscripttypes.typetables("py-appscript")
class RbAppscriptParser(_AppscriptParser):
	_asname = staticmethod(makeidentifier.getconverter("rb-appscript"))
	typemodule = appscripttypes.typetables("rb-appscript")
_parsers = {"applescript": AppleScriptParser, "appscript": PyAppscriptParser, "objc-appscript": ObjCAppscriptParser, "py-appscript": PyAppscriptParser, "rb-appscript": RbAppscriptParser}
def parseaetes(aetes, path="", style="appscript"):
	p = _parsers[style](path)
	aeteparser.parse(aetes, p)
	return p.result()
def parselang(code="ascr", style="appscript"):
	return parseaetes(getsysterminology(code), "", style)
def parsefile(paths, style="appscript"):
	if isinstance(paths, basestring):
		paths = [paths]
	aetes = []
	for path in paths:
		f = file(path)
		aetes.append(newdesc(kae.typeAETE, f.read()))
		f.close()
	return parseaetes(aetes, paths[0], style)
def parseapp(path, style="appscript"):
	return parseaetes(getappterminology(path), path, style)