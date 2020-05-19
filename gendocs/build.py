try:
	pass
except ImportError:
	pass
EXPECTED_VERSION_SUFFIX = "-quilt3"
GH_HTTPS_REV = "quilt"
if __name__ == "__main__":
	try:
		pydocmd_dist = pkg_resources.get_distribution("pydoc-markdown")
		version = pydocmd_dist.version
	except pkg_resources.DistributionNotFound:
		version = ""
	if not version.endswith(EXPECTED_VERSION_SUFFIX):
		valid_input = ["y", "n", "yes", "no"]
		response = ""
		while response not in valid_input:
			print("\nUsing {!r}:".format(sys.executable))
			if version:
				print("This will uninstall the existing version of pydoc-markdown ({}) first.".format(version))
			sys.stdout.flush()
			sys.stderr.flush()
			response = input("    Install quilt-specific pydoc-markdown? (y/n): ").lower()
		if response in ["n", "no"]:
			print("exiting..")
			exit()
		if version:
			pipmain(["uninstall", "pydoc-markdown"])
		pipmain(["install", f"git+https://github.com/quiltdata/pydoc-markdown.git@{GH_HTTPS_REV}"])
	if not pydocmd.__version__.endswith(EXPECTED_VERSION_SUFFIX):
		print("Please re-run this script to continue")
		exit()
	if sys.argv[-1].endswith("build.py"):
		sys.argv.append("build")
	else:
		print("Using custom args for mkdocs.")
	pydocmd_main()
	pydocmd_config = yaml.safe_load(open("pydocmd.yml"))
	print("Generated HTML in {!r}".format(pydocmd_config.get("site_dir")))
	print("Generated markdown in {!r}".format(pydocmd_config.get("gens_dir")))