te = app("TextEdit")
s = te.documents[1].text.get()
for c, r in [("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ("\t", "    ")]:
	s = s.replace(c, r)
te.documents[1].text.set(s)