from sys import stdout
class _Out:
	def write(self, s):
		stdout.write(s.encode("utf8", "replace"))
class TextRenderer:
	def __init__(self, out=_Out()):
		self.output = out
		self.indent = ""
		self._pad = False
	def add(self, name, type, ismany, islast, tbc=False):
		if self._pad:
			print >>self.output, "    " + self.indent
			self._pad = False
		print >>self.output, "    %s%s%s%s%s" % (self.indent, ismany and "=" or "-", name, type and " <%s>" % type or "", tbc and " ->" or "")
		if islast and self.indent:
			self.indent = self.indent[:-4] + "    "
	def down(self):
		self.indent += "   |"
	def up(self):
		self.indent = self.indent[:-4]
		self._pad = True
class RelationshipGrapher:
	def __init__(self, terms, renderer):
		self.terms = terms
		self.renderer = renderer
		self.relationshipcache = {}
	def _relationships(self, klass):
		if not self.relationshipcache.has_key(klass.name):
			klass = klass.full()
			properties = [o for o in klass.properties() if o.type.realvalue().kind == "class"]
			elements = list(klass.elements())
			self.relationshipcache[klass.name] = (properties, elements)
		return self.relationshipcache[klass.name]
	def _hasrelationships(self, klass):
		p, e = self._relationships(klass)
		return bool(p or e)
	def draw(self, classname="application", maxdepth=3):
		def render(klass, visitedproperties, visitedelements, maxdepth):
			properties, elements = self._relationships(klass)
			if properties or elements:
				allvisitedproperties = visitedproperties + [o.type for o in properties]
				allvisitedelements = visitedelements + [o.type for o in elements]
				self.renderer.down()
				for i, prop in enumerate(properties):
					propclass = prop.type.realvalue()
					iscontinued = (prop.type in visitedproperties or prop.type in allvisitedelements or maxdepth < 2) and self._hasrelationships(propclass)
					self.renderer.add(prop.name, propclass.name, False, i == len(properties) and not elements, iscontinued)
					if not iscontinued:
						render(propclass, allvisitedproperties, allvisitedelements, maxdepth - 1)
				for i, elem in enumerate(elements):
					elemclass = elem.type.realvalue()
					iscontinued = (elem.type in visitedelements or maxdepth < 2) and self._hasrelationships(elemclass)
					self.renderer.add(elem.name, None, True, i == len(elements), iscontinued)
					if not iscontinued:
						render(elemclass, allvisitedproperties, allvisitedelements, maxdepth - 1)
				self.renderer.up()
		klass = self.terms.classes().byname(classname)
		self.renderer.add(classname, None, False, False)
		render(klass, [], [], maxdepth)