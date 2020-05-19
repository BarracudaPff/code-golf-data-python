def check_dependencies(settings):
	pyver = sys.version_info[:2]
	if pyver < PYTHON_2_MIN_VERSION or (3, 0) <= pyver < PYTHON_3_MIN_VERSION:
		dependency_error("Python %s or %s+ is required." % (PYTHON_2_MIN_VERSION_STR, PYTHON_3_MIN_VERSION_STR))
	if not is_exe_in_path("node"):
		dependency_error("node (from NodeJS) was not found. It must be " "installed from your package manager or from " "https://nodejs.org/")
	if not os.path.exists("node_modules"):
		dependency_error("The node_modules directory is missing. Please " "re-run `./setup.py develop` to install all NodeJS " "dependencies.")
	for key in ("UGLIFYJS_BINARY", "LESS_BINARY", "BABEL_BINARY"):
		path = settings.PIPELINE[key]
		if not os.path.exists(path):
			dependency_error("%s is missing. Please re-run `./setup.py " "develop` to install all NodeJS dependencies." % os.path.abspath(path))
	if not has_module("pysvn") and not has_module("subvertpy"):
		dependency_warning("Neither the subvertpy nor pysvn Python modules " "were found. Subversion integration will not work. " "For pysvn, see your package manager for the " "module or download from " "http://pysvn.tigris.org/project_downloads.html. " "For subvertpy, run `pip install subvertpy`. We " "recommend pysvn for better compatibility.")
	if has_module("P4"):
		try:
			subprocess.call(["p4", "-h"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		except OSError:
			dependency_warning("The p4 command not found. Perforce " "integration will not work. To enable support, " "download p4 from " "http://cdist2.perforce.com/perforce/ and " "place it in your PATH.")
	else:
		dependency_warning("The p4python module was not found. Perforce " "integration will not work. To enable support, " "run `pip install p4python`")
	if not is_exe_in_path("hg"):
		dependency_warning("The hg command was not found. Mercurial " "integration will not work. To enable support, " "run `pip install mercurial`")
	if not is_exe_in_path("bzr"):
		dependency_warning("The bzr command was not found. Bazaar integration " "will not work. To enable support, run " "`pip install bzr`")
	if not is_exe_in_path("cvs"):
		dependency_warning("The cvs command was not found. CVS integration " "will not work. To enable support, install cvs " "from your package manager or from " "http://www.nongnu.org/cvs/")
	if not is_exe_in_path("git"):
		dependency_warning("The git command not found. Git integration " "will not work. To enable support, install git " "from your package manager or from " "https://git-scm.com/downloads")
	fail_if_missing_dependencies()
def upgrade_database():
	"""Perform an upgrade of the database.
    This will prompt the user for confirmation, with instructions on what
    will happen. If the database is using SQLite3, it will be backed up
    automatically, making a copy that contains the current timestamp.
    Otherwise, the user will be prompted to back it up instead.
    Returns:
        bool:
        ``True`` if the user has confirmed the upgrade. ``False`` if they
        have not.
    """
	database = settings.DATABASES["default"]
	db_name = database["NAME"]
	backup_db_name = None
	if "--no-backup" not in sys.argv and database["ENGINE"] == "django.db.backends.sqlite3" and os.path.exists(db_name):
		backup_db_name = "%s.%s" % (db_name, datetime.now().strftime("%Y%m%d.%H%M%S"))
		try:
			shutil.copy(db_name, backup_db_name)
		except Exception as e:
			sys.stderr.write("Unable to make a backup of your database at " "%s: %s\n\n" % (db_name, e))
			backup_db_name = None
	if "--noinput" in sys.argv:
		if backup_db_name:
			print("Your existing database has been backed up to\n" "%s\n" % backup_db_name)
		perform_upgrade = True
	else:
		message = "You are about to upgrade your database, which cannot be undone." "\n\n"
		if backup_db_name:
			message += "Your existing database has been backed up to\n" "%s" % backup_db_name
		else:
			message += "PLEASE MAKE A BACKUP BEFORE YOU CONTINUE!"
		message += '\n\nType "yes" to continue or "no" to cancel: '
		perform_upgrade = input(message).lower() in ("yes", "y")
		print("\n")
	if perform_upgrade:
		print("===========================================================\n" 'Performing the database upgrade. Any "unapplied evolutions"\n' "will be handled automatically.\n" "===========================================================\n")
		commands = [["evolve", "--noinput", "--execute"]]
		for command in commands:
			execute_from_command_line([sys.argv[0]] + command)
	else:
		print("The upgrade has been cancelled.\n")
		sys.exit(1)
def main(settings, in_subprocess):
	if dirname(settings.__file__) == os.getcwd():
		sys.stderr.write("manage.py should not be run from within the " "'reviewboard' Python package directory.\n")
		sys.stderr.write("Make sure to run this from the top of the " "Review Board source tree.\n")
		sys.exit(1)
	try:
		command_name = sys.argv[1]
	except IndexError:
		command_name = None
	if command_name in ("runserver", "test"):
		if settings.DEBUG and not in_subprocess:
			sys.stderr.write("Running dependency checks (set DEBUG=False " "to turn this off)...\n")
			check_dependencies(settings)
		if command_name == "runserver":
			simple_server.ServerHandler.http_version = "1.1"
	elif command_name not in ("evolve", "syncdb", "migrate"):
		initialize()
		if command_name == "upgrade":
			upgrade_database()
			return
	execute_from_command_line(sys.argv)
def run():
	sys.path.insert(0, dirname(dirname(abspath(__file__))))
	try:
		sys.path.remove(dirname(abspath(__file__)))
	except ValueError:
		pass
	if str("DJANGO_SETTINGS_MODULE") not in os.environ:
		in_subprocess = False
		os.environ[str("DJANGO_SETTINGS_MODULE")] = str("reviewboard.settings")
	else:
		in_subprocess = True
	if len(sys.argv) > 1 and sys.argv[1] == "test":
		os.environ[str("RB_RUNNING_TESTS")] = str("1")
	try:
		pass
	except ImportError as e:
		sys.stderr.write("Error: Can't find the file 'settings.py' in the " "directory containing %r. It appears you've " "customized things.\n" "You'll have to run django-admin.py, passing it your " "settings module.\n" "(If the file settings.py does indeed exist, it's " "causing an ImportError somehow.)\n" % __file__)
		sys.stderr.write("The error we got was: %s\n" % e)
		sys.exit(1)
	main(settings, in_subprocess)
if __name__ == "__main__":
	run()