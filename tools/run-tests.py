import argparse
import os
import subprocess
import sys
from settings import *
OUTPUT_DIR = path.join(PROJECT_DIR, "build", "tests")
parser = argparse.ArgumentParser()
parser.add_argument("--toolchain", action="store", default="", help="Add toolchain file")
parser.add_argument("--outdir", action="store", default=OUTPUT_DIR, help="Specify output directory (default: %(default)s)")
parser.add_argument("--check-signed-off", action="store_true", default=False, help="Run signed-off check")
parser.add_argument("--check-signed-off-tolerant", action="store_true", default=False, help="Run signed-off check in tolerant mode")
parser.add_argument("--check-signed-off-travis", action="store_true", default=False, help="Run signed-off check in tolerant mode if on Travis CI and not checking a pull request")
parser.add_argument("--check-cppcheck", action="store_true", default=False, help="Run cppcheck")
parser.add_argument("--check-vera", action="store_true", default=False, help="Run vera check")
parser.add_argument("--check-license", action="store_true", default=False, help="Run license check")
parser.add_argument("--buildoption-test", action="store_true", default=False, help="Run buildoption-test")
parser.add_argument("--jerry-tests", action="store_true", default=False, help="Run jerry-tests")
parser.add_argument("--jerry-test-suite", action="store_true", default=False, help="Run jerry-test-suite")
parser.add_argument("--unittests", action="store_true", default=False, help="Run unittests")
parser.add_argument("--precommit", action="store_true", default=False, dest="all", help="Run all test")
if len(sys.argv) == 1:
	parser.print_help()
	sys.exit(1)
script_args = parser.parse_args()
if path.isabs(script_args.outdir):
	OUTPUT_DIR = script_args.outdir
else:
	OUTPUT_DIR = path.join(PROJECT_DIR, script_args.outdir)
class Options:
	out_dir = ""
	build_args = []
	test_args = []
	def __init__(self, name="", build_args=[], test_args=[]):
		self.out_dir = path.join(OUTPUT_DIR, name)
		self.build_args = build_args
		self.build_args.append("--builddir=%s" % self.out_dir)
		self.test_args = test_args
jerry_unittests_options = [Options("unittests", ["--unittests", "--error-messages=on", "--snapshot-save=on", "--snapshot-exec=on"]), Options("unittests-debug", ["--unittests", "--debug", "--error-messages=on", "--snapshot-save=on", "--snapshot-exec=on"])]
jerry_tests_options = [Options("jerry_tests"), Options("jerry_tests-snapshot", ["--snapshot-save=on", "--snapshot-exec=on"], ["--snapshot"]), Options("jerry_tests-debug", ["--debug"]), Options("jerry_tests-debug-snapshot", ["--debug", "--snapshot-save=on", "--snapshot-exec=on"], ["--snapshot"])]
jerry_test_suite_options = jerry_tests_options[:]
jerry_test_suite_options.append(Options("jerry_test_suite-minimal", ["--profile=minimal"]))
jerry_test_suite_options.append(Options("jerry_test_suite-minimal-snapshot", ["--profile=minimal", "--snapshot-save=on", "--snapshot-exec=on"], ["--snapshot"]))
jerry_test_suite_options.append(Options("jerry_test_suite-minimal-debug", ["--debug", "--profile=minimal"]))
jerry_test_suite_options.append(Options("jerry_test_suite-minimal-debug-snapshot", ["--debug", "--profile=minimal", "--snapshot-save=on", "--snapshot-exec=on"], ["--snapshot"]))
jerry_buildoptions = [Options("buildoption_test-lto", ["--lto=on"]), Options("buildoption_test-error_messages", ["--error-messages=on"]), Options("buildoption_test-all_in_one", ["--all-in-one=on"]), Options("buildoption_test-valgrind", ["--valgrind=on"]), Options("buildoption_test-valgrind_freya", ["--valgrind-freya=on"]), Options("buildoption_test-mem_stats", ["--mem-stats=on"]), Options("buildoption_test-show_opcodes", ["--show-opcodes=on"]), Options("buildoption_test-show_regexp_opcodes", ["--show-regexp-opcodes=on"]), Options("buildoption_test-compiler_default_libc", ["--jerry-libc=off"])]
def get_bin_dir_path(out_dir):
	return path.join(out_dir, "bin")
def get_binary_path(out_dir):
	return path.join(get_bin_dir_path(out_dir), "jerry")
def create_binary(buildoptions):
	build_cmd = [BUILD_SCRIPT]
	build_cmd.extend(buildoptions)
	if script_args.toolchain:
		build_cmd.append("--toolchain=%s" % script_args.toolchain)
	sys.stderr.write("Build command: %s\n" % " ".join(build_cmd))
	try:
		script_output = subprocess.check_output(build_cmd)
	except subprocess.CalledProcessError as e:
		return e.returncode
	return 0
def run_check(runnable):
	sys.stderr.write("Test command: %s\n" % " ".join(runnable))
	try:
		ret = subprocess.check_call(runnable)
	except subprocess.CalledProcessError as e:
		return e.returncode
	return ret
def run_jerry_tests():
	ret_build = ret_test = 0
	for job in jerry_tests_options:
		ret_build = create_binary(job.build_args)
		if ret_build:
			break
		test_cmd = [TEST_RUNNER_SCRIPT, get_binary_path(job.out_dir), JERRY_TESTS_DIR]
		if job.test_args:
			test_cmd.extend(job.test_args)
		ret_test |= run_check(test_cmd)
	return ret_build | ret_test
def run_jerry_test_suite():
	ret_build = ret_test = 0
	for job in jerry_test_suite_options:
		ret_build = create_binary(job.build_args)
		if ret_build:
			break
		test_cmd = [TEST_RUNNER_SCRIPT, get_binary_path(job.out_dir)]
		if "--profile=minimal" in job.build_args:
			test_cmd.append(JERRY_TEST_SUITE_MINIMAL_LIST)
		else:
			test_cmd.append(JERRY_TEST_SUITE_DIR)
		if job.test_args:
			test_cmd.extend(job.test_args)
		ret_test |= run_check(test_cmd)
	return ret_build | ret_test
def run_unittests():
	ret_build = ret_test = 0
	for job in jerry_unittests_options:
		ret_build = create_binary(job.build_args)
		if ret_build:
			break
		ret_test |= run_check([UNITTEST_RUNNER_SCRIPT, get_bin_dir_path(job.out_dir)])
	return ret_build | ret_test
def run_buildoption_test():
	for job in jerry_buildoptions:
		ret = create_binary(job.build_args)
		if ret:
			break
	return ret
def main():
	ret = 0
	if script_args.check_signed_off_tolerant:
		ret = run_check([SIGNED_OFF_SCRIPT, "--tolerant"])
	if not ret and script_args.check_signed_off_travis:
		ret = run_check([SIGNED_OFF_SCRIPT, "--travis"])
	if not ret and (script_args.all or script_args.check_signed_off):
		ret = run_check([SIGNED_OFF_SCRIPT])
	if not ret and (script_args.all or script_args.check_cppcheck):
		ret = run_check([CPPCHECK_SCRIPT])
	if not ret and (script_args.all or script_args.check_vera):
		ret = run_check([VERA_SCRIPT])
	if not ret and (script_args.all or script_args.check_license):
		ret = run_check([LICENSE_SCRIPT])
	if not ret and (script_args.all or script_args.jerry_tests):
		ret = run_jerry_tests()
	if not ret and (script_args.all or script_args.jerry_test_suite):
		ret = run_jerry_test_suite()
	if not ret and (script_args.all or script_args.unittests):
		ret = run_unittests()
	if not ret and (script_args.all or script_args.buildoption_test):
		ret = run_buildoption_test()
	sys.exit(ret)
if __name__ == "__main__":
	main()