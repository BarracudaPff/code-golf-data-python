codecs = Codecs()
ascr = OSAComponentInstance(OpenDefaultComponent("osa ", "ascr"))
names = codecs.unpack(ascr.ASGetSourceStyleNames(kOSAModeNull))
values = codecs.unpack(ascr.ASGetSourceStyles())
pprint(zip(names, values))
values[0][AEType("ptsz")] = 42
ascr.ASSetSourceStyles(codecs.pack(values))
values = codecs.unpack(ascr.ASGetSourceStyles())
pprint(zip(names, values))