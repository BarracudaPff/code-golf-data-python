"""osaterminology.tables.tableparser -- builds tables similar to those used by appscript itself; based on py-appscript's terminologyparser module
(C) 2008 HAS
"""
try:
	set
except NameError:
	pass
__all__ = ["buildtablesforaetes"]
class TerminologyTableReceiver(Receiver):
	def __init__(self, style):
		self.convert = getconverter(style)
		self.commands = {}
		self.properties = []
		self.elements = []
		self.classes = []
		self.enumerators = []
		self._foundproperties = set()
		self._foundelements = set()
		self._foundclasses = set()
		self._foundenumerators = set()
		self._spareclassnames = {}
		self._foundclasscodes = set()
		self._foundelementcodes = set()
	def start_command(self, code, name, description, directarg, reply):
		self.commandargs = []
		if not self.commands.has_key(name) or self.commands[name][1] == code:
			self.commands[name] = (self.convert(name), code, self.commandargs)
	def add_labelledarg(self, code, name, description, datatype, isoptional, islist, isenum):
		self.commandargs.append((self.convert(name), code))
	def start_class(self, code, name, description):
		self.classname = self.convert(name)
		self.classcode = code
		self.isplural = False
		self._spareclassnames[code] = self.classname
	def is_plural(self):
		self.isplural = True
	def add_property(self, code, name, description, datatype, islist, isenum, ismutable):
		if name + code not in self._foundproperties:
			self.properties.append((self.convert(name), code))
			self._foundproperties.add(name + code)
	def end_class(self):
		name, code = self.classname, self.classcode
		if self.isplural:
			if name + code not in self._foundelements:
				self.elements.append((name, code))
				self._foundelements.add(name + code)
				self._foundelementcodes.add(code)
		else:
			if name + code not in self._foundclasses:
				self.classes.append((name, code))
				self._foundclasses.add(name + code)
				self._foundclasscodes.add(code)
	def add_enumerator(self, code, name, description):
		if name + code not in self._foundenumerators:
			self.enumerators.append((self.convert(name), code))
			self._foundenumerators.add(name + code)
	def result(self):
		missingElements = self._foundclasscodes - self._foundelementcodes
		missingClasses = self._foundelementcodes - self._foundclasscodes
		for code in missingElements:
			self.elements.append((self._spareclassnames[code], code))
		for code in missingClasses:
			self.classes.append((self._spareclassnames[code], code))
		return (self.classes, self.enumerators, self.properties, self.elements, self.commands.values())
def buildtablesforaetes(aetes, style="py-appscript"):
	"""
		aetes : list of AEDesc
		style : str
	"""
	receiver = TerminologyTableReceiver(style)
	parse(aetes, receiver)
	return receiver.result()