"""
cg file parse to cfg model
TODO...
- handle parse of ned forms
@author: snellenbach
"""
class CfgExtractor:
	def __init__(self, fName):
		in_fs = FileStream(fName)
		lexer = ConfigLexer(in_fs)
		stream = CommonTokenStream(lexer)
		parser = ConfigParser(stream)
		tree = parser.root()
		builder = CfgModelBuilder()
		walker = ParseTreeWalker()
		walker.walk(builder, tree)
		self.modelRoot = builder.rootCfgNode
	def getModel(self):
		return self.modelRoot