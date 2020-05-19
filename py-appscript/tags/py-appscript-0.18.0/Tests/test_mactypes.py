class TC_MacTypes(unittest.TestCase):
	dir = "/private/tmp"
	def setUp(self):
		self.path1 = os.tempnam(self.dir, "py-mactypes-test.")
		file(self.path1, "w").close()
		fname = os.path.split(self.path1)[1]
		self.path2 = os.path.join(self.dir, "moved-" + fname)
	def test_alias(self):
		self.f = mactypes.Alias(self.path1)
		self.assertEqual("mactypes.Alias(u%r)" % self.path1, repr(self.f))
		self.assertEqual(self.path1, self.f.path)
		self.assertEqual("alis", self.f.aedesc.type)
		os.rename(self.path1, self.path2)
		self.assertEqual(self.path2, self.f.path)
		self.assertEqual("mactypes.Alias(u%r)" % self.path2, repr(self.f))
		os.remove(self.path2)
		self.assertRaises(MacOS.Error, lambda: self.f.path)
		self.assertRaises(MacOS.Error, lambda: self.f.file)
	def test_fileURL(self):
		g = mactypes.File("/non/existent path")
		self.assertEqual("/non/existent path", g.path)
		self.assertEqual("furl", g.aedesc.type)
		self.assertEqual("file://localhost/non/existent%20path", g.aedesc.data)
		self.assertEqual("mactypes.File(u'/non/existent path')", repr(g.file))
		self.assertRaises(MacOS.Error, lambda: g.fsalias)
if __name__ == "__main__":
	unittest.main()