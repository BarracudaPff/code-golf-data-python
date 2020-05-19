"""terminology -- Obtains an application's aete resource(s) using a 'ascrgdte' event and converts them into lookup tables for use in AppData objects.
(C) 2004-2008 HAS
"""
from aem import AEType, AEEnum, EventError, findapp, ae, kae
from . import defaultterminology
from .terminologyparser import buildtablesforaetes
from .keywordwrapper import Keyword
__all__ = ["tablesforapp", "tablesformodule", "tablesforaetes", "kProperty", "kElement", "kCommand", "defaulttables", "aetesforapp", "dump"]
kProperty = b"p"
kElement = b"e"
kCommand = b"c"
_terminologycache = {}
_defaulttypebyname = {}
_defaulttypebycode = {}
_defaulttypecodebyname = {}
for _, enumerators in defaultterminology.enumerations:
	for name, code in enumerators:
		_defaulttypebyname[name] = AEEnum(code)
		_defaulttypebycode[code] = Keyword(name)
		_defaulttypecodebyname[name] = code
for defs in [defaultterminology.types, defaultterminology.properties]:
	for name, code in defs:
		_defaulttypebyname[name] = AEType(code)
		_defaulttypebycode[code] = Keyword(name)
		_defaulttypecodebyname[name] = code
_defaultreferencebycode = {}
_defaultreferencebyname = {}
_defaultcommandcodebyname = {}
for name, code in defaultterminology.properties:
	_defaultreferencebycode[kProperty + code] = (kProperty, name)
	_defaultreferencebyname[name] = (kProperty, code)
for name, code in defaultterminology.elements:
	_defaultreferencebycode[kElement + code] = (kElement, name)
	_defaultreferencebyname[name] = (kElement, code)
for name, code, params in defaultterminology.commands:
	_defaultreferencebyname[name] = (kCommand, (code, dict(params)))
	_defaultcommandcodebyname[name] = code
def _maketypetable(classes, enums, properties):
	typebycode = _defaulttypebycode.copy()
	typebyname = _defaulttypebyname.copy()
	for klass, table in [(AEEnum, enums), (AEType, properties), (AEType, classes)]:
		for i, (name, code) in enumerate(table):
			if _defaulttypecodebyname.get(name, code) != code:
				name += "_"
			typebycode[code] = Keyword(name)
			name, code = table[-i - 1]
			if _defaulttypecodebyname.get(name, code) != code:
				name += "_"
			typebyname[name] = klass(code)
	return typebycode, typebyname
def _makereferencetable(properties, elements, commands):
	referencebycode = _defaultreferencebycode.copy()
	referencebyname = _defaultreferencebyname.copy()
	for kind, table in [(kElement, elements), (kProperty, properties)]:
		for i, (name, code) in enumerate(table):
			if _defaulttypecodebyname.get(name, code) != code:
				name += "_"
			referencebycode[kind + code] = (kind, name)
			name, code = table[-i - 1]
			if _defaulttypecodebyname.get(name, code) != code:
				name += "_"
			referencebyname[name] = (kind, code)
	if "text" in referencebyname:
		referencebyname["text"] = (kElement, referencebyname["text"][1])
	for name, code, args in commands[::-1]:
		if code != _defaultcommandcodebyname.get(name, code):
			name += "_"
		referencebyname[name] = (kCommand, (code, dict(args)))
	return referencebycode, referencebyname
defaulttables = _maketypetable([], [], []) + _makereferencetable([], [], [])
def aetesforapp(aemapp):
	"""Get aetes from local/remote app via an ascrgdte event; result is a list of byte strings."""
	try:
		aetes = aemapp.event(b"ascrgdte", {b"----": 0}).send(120 * 60)
	except Exception as e:
		if isinstance(e, EventError) and e.errornumber == -192:
			aetes = []
		else:
			raise RuntimeError("Can't get terminology for application (%r): %s" % (aemapp, e))
	if not isinstance(aetes, list):
		aetes = [aetes]
	return [aete for aete in aetes if isinstance(aete, ae.AEDesc) and aete.type == kae.typeAETE and aete.data]
def tablesforaetes(aetes):
	"""Build terminology tables from a list of unpacked aete byte strings.
		Result : tuple of dict -- (typebycode, typebyname, referencebycode, referencebyname)
	"""
	classes, enums, properties, elements, commands = buildtablesforaetes(aetes)
	return _maketypetable(classes, enums, properties) + _makereferencetable(properties, elements, commands)
def tablesformodule(terms):
	"""Build terminology tables from a dumped terminology module.
		Result : tuple of dict -- (typebycode, typebyname, referencebycode, referencebyname)
	"""
	return _maketypetable(terms.classes, terms.enums, terms.properties) + _makereferencetable(terms.properties, terms.elements, terms.commands)
def tablesforapp(aemapp):
	"""Build terminology tables for an application.
		aemapp : aem.Application
		Result : tuple of dict -- (typebycode, typebyname, referencebycode, referencebyname)
	"""
	if aemapp.AEM_identity not in _terminologycache:
		_terminologycache[aemapp.AEM_identity] = tablesforaetes(aetesforapp(aemapp))
	return _terminologycache[aemapp.AEM_identity]
def dump(apppath, modulepath):
	"""Dump terminology data to Python module.
		apppath : str -- name or path of application
		modulepath : str -- path to generated module
	Generates a Python module containing an application's basic terminology
	(names and codes) as used by appscript.
	Call the dump() function to dump faulty aetes to Python module, e.g.:
		dump('MyApp', '/Library/Python/2.5/site-packages/myappglue.py')
	Patch any errors by hand, then import the patched module into your script
	and pass it to appscript's app() constructor via its 'terms' argument, e.g.:
		from appscript import *
		import myappglue
		myapp = app('MyApp', terms=myappglue)
	Note that dumped terminologies aren't used by appscript's built-in help system.
	"""
	from pprint import pprint
	from sys import argv
	apppath = findapp.byname(apppath)
	tables = buildtablesforaetes(ae.getappterminology(apppath))
	atts = zip(("classes", "enums", "properties", "elements", "commands"), tables)
	f = open(modulepath, "w")
	f.write("version = 1.1\n")
	f.write("path = %r\n" % apppath)
	for key, value in atts:
		if key[0] != "_":
			f.write("\n%s = \\\n" % key)
			pprint(value, f)
	f.close()