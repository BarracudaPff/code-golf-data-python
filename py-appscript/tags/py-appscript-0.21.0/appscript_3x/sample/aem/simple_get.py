import aem
textedit = aem.Application("/Applications/TextEdit.app")
print(textedit.event(b"coregetd", {b"----": aem.app.property(b"pnam")}).send())
finder = aem.Application(aem.findapp.byname("Finder"))
print(finder.event(b"coregetd", {b"----": aem.app.property(b"home").elements(b"cobj"), aem.kae.keyAERequestedType: aem.AEType(aem.kae.typeAlias)}).send())