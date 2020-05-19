class TC_MacTypes(unittest.TestCase):
	dir = "/private/tmp"
	def setUp(self):
		self.path1 = tempfile.mkstemp("", "py-mactypes-test.", self.dir)[1]
		open(self.path1, "w").close()
		fname = os.path.split(self.path1)[1]
		self.path2 = os.path.join(self.dir, "moved-" + fname)
	def test_alias(self):
		self.f = mactypes.Alias(self.path1)
		path1 = self.path1
		if not path1.startswith("/private/"):
			path1 = "/private" + path1
		self.assertEqual("mactypes.Alias(%r)" % path1, repr(self.f))
		self.assertEqual(path1, self.f.path)
		self.assertEqual(b"alis", self.f.desc.type)
		os.rename(path1, self.path2)
		self.assertEqual(self.path2, self.f.path)
		self.assertEqual("mactypes.Alias(%r)" % self.path2, repr(self.f))
		os.remove(self.path2)
		self.assertRaises(MacOSError, lambda: self.f.path)
		self.assertRaises(MacOSError, lambda: self.f.file)
	def test_fileURL(self):
		g = mactypes.File("/non/existent path")
		self.assertEqual("/non/existent path", g.path)
		self.assertEqual(b"furl", g.desc.type)
		self.assertEqual("file://localhost/non/existent%20path", g.desc.data.decode("utf8"))
		self.assertEqual("mactypes.File('/non/existent path')", repr(g.file))
		self.assertRaises(MacOSError, lambda: g.alias)
if __name__ == "__main__":
	unittest.main()