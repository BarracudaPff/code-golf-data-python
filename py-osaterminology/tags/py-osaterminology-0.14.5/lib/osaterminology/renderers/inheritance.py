"""inheritance"""
from sys import stdout
class _Out:
	def write(self, s):
		stdout.write(s.encode("utf8", "replace"))
class TextRenderer:
	def __init__(self, out=_Out()):
		self._output = out
		self._indent = ""
		self._pad = False
	def add(self, name, islast, hilite=False, tbc=False):
		if self._pad:
			print >>self._output, "    " + self._indent
			self._pad = False
		print >>self._output, " %s %s-%s%s" % (hilite and "->" or "  ", self._indent, name, tbc and " ->" or "")
		if islast and self._indent:
			self._indent = self._indent[:-4] + "    "
	def down(self):
		self._indent += "   |"
	def up(self):
		self._indent = self._indent[:-4]
		self._pad = True
class InheritanceGrapher:
	def __init__(self, terms, renderer):
		self.terms = terms
		self.renderer = renderer
		self.childrenByClassName = self._findChildren()
	def _findChildren(self):
		classes = self.terms.classes()
		childrenByClassName = dict([(name, []) for name in classes.names()])
		for klass in classes:
			for superclass in klass.parents():
				try:
					lst = childrenByClassName[superclass.name]
				except KeyError:
					continue
				if klass.name not in lst and klass.name != superclass.name:
					lst.append(klass.name)
		return childrenByClassName
	def _findParents(self, klass, children, result):
		if klass.parents():
			for parentClass in klass.parents():
				lst = children[:]
				if parentClass.name not in lst:
					lst.insert(0, parentClass.name)
				self._findParents(parentClass, lst, result)
		else:
			result.append(children)
	def _renderSubclasses(self, names, visited):
		for i, name in enumerate(names):
			islast = i + 1 == len(names)
			self.renderer.add(name, islast, tbc=name in visited and self.childrenByClassName[name])
			if name not in visited:
				visited.append(name)
				if self.childrenByClassName.get(name):
					self.renderer.down()
					self._renderSubclasses(self.childrenByClassName[name], visited)
					self.renderer.up()
	def draw(self, classname=None):
		if classname:
			thisClass = self.terms.classes().byname(classname).collapse()
			parentLists = []
			self._findParents(thisClass, [thisClass.name], parentLists)
			for i, lst in enumerate(parentLists):
				for name in lst[:-1]:
					self.renderer.add(name, True)
					self.renderer.down()
				if not i:
					self.renderer.add(thisClass.name, True, True)
					self.renderer.down()
					self._renderSubclasses(self.childrenByClassName[classname], [])
					self.renderer.up()
				else:
					self.renderer.add(thisClass.name, True, False, True)
				for _ in lst[:-1]:
					self.renderer.up()
		else:
			for klass in self.terms.classes():
				if not [o for o in klass.parents() if o.kind == "class"]:
					self._renderSubclasses([klass.name], [])