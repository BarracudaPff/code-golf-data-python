try:
	unicode("foo", "euc-jp")
except LookupError:
	raise TestSkipped
class TestEmailAsianCodecs(TestEmailBase):
	def test_japanese_codecs(self):
		eq = self.ndiffAssertEqual
		j = Charset("euc-jp")
		g = Charset("iso-8859-1")
		h = Header("Hello World!")
		jhello = "\xa5\xcf\xa5\xed\xa1\xbc\xa5\xef\xa1\xbc\xa5\xeb\xa5\xc9\xa1\xaa"
		ghello = "Gr\xfc\xdf Gott!"
		h.append(jhello, j)
		h.append(ghello, g)
		eq(
			h.encode(),
			"""\
Hello World! =?iso-2022-jp?b?GyRCJU8lbSE8JW8hPCVrJUkhKhsoQg==?=
 =?iso-8859-1?q?Gr=FC=DF?= =?iso-8859-1?q?_Gott!?=""",
		)
		eq(decode_header(h.encode()), [("Hello World!", None), ("\x1b$B%O%m!<%o!<%k%I!*\x1b(B", "iso-2022-jp"), ("Gr\xfc\xdf Gott!", "iso-8859-1")])
		long = "test-ja \xa4\xd8\xc5\xea\xb9\xc6\xa4\xb5\xa4\xec\xa4\xbf\xa5\xe1\xa1\xbc\xa5\xeb\xa4\xcf\xbb\xca\xb2\xf1\xbc\xd4\xa4\xce\xbe\xb5\xc7\xa7\xa4\xf2\xc2\xd4\xa4\xc3\xa4\xc6\xa4\xa4\xa4\xde\xa4\xb9"
		h = Header(long, j, header_name="Subject")
		enc = h.encode()
		eq(
			enc,
			"""\
=?iso-2022-jp?b?dGVzdC1qYSAbJEIkWEVqOUYkNSRsJD8lYSE8JWskTztKGyhC?=
 =?iso-2022-jp?b?GyRCMnE8VCROPjVHJyRyQlQkQyRGJCQkXiQ5GyhC?=""",
		)
		eq(h.__unicode__().encode("euc-jp"), long)
	def test_payload_encoding(self):
		jhello = "\xa5\xcf\xa5\xed\xa1\xbc\xa5\xef\xa1\xbc\xa5\xeb\xa5\xc9\xa1\xaa"
		jcode = "euc-jp"
		msg = Message()
		msg.set_payload(jhello, jcode)
		ustr = unicode(msg.get_payload(), msg.get_content_charset())
		self.assertEqual(jhello, ustr.encode(jcode))
def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(TestEmailAsianCodecs))
	return suite
def test_main():
	run_unittest(TestEmailAsianCodecs)
if __name__ == "__main__":
	unittest.main(defaultTest="suite")