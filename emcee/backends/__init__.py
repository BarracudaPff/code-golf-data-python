__all__ = ["Backend", "HDFBackend", "TempHDFBackend", "get_test_backends"]
def get_test_backends():
	backends = [Backend]
	try:
		pass
	except ImportError:
		pass
	else:
		backends.append(TempHDFBackend)
	return backends