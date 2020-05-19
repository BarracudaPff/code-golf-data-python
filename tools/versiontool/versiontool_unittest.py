"""Tests for VersionTool."""
import io
import json
import unittest
try:
	import StringIO
except ImportError:
	StringIO = None
from build_bazel_rules_apple.tools.versiontool import versiontool
def _str_io(*args, **kwargs):
	"""Helper for PY2/Py3 StringIO"""
	if StringIO:
		return StringIO.StringIO(*args, **kwargs)
	return io.StringIO(*args, **kwargs)
class VersionToolTest(unittest.TestCase):
	def _assert_versiontool_result(self, control, expected):
		"""Asserts that VersionTool's result equals the expected dictionary.
    Args:
      control: The control struct to pass to VersionTool. See the module doc for
          the versiontool module for a description of this format.
      expected: The dictionary that represents the expected result from running
          VersionTool.
    """
		outdict = versiontool.VersionTool(control).run()
		self.assertEqual(expected, outdict)
	def test_simple_versions(self):
		self._assert_versiontool_result({"build_version_pattern": "1.2", "short_version_string_pattern": "1.2.3"}, {"build_version": "1.2", "short_version_string": "1.2.3"})
	def test_simple_build_version_is_also_short_version_string(self):
		self._assert_versiontool_result({"build_version_pattern": "1.2"}, {"build_version": "1.2", "short_version_string": "1.2"})
	def test_build_label_substitution(self):
		self._assert_versiontool_result({"build_info_path": _str_io("BUILD_EMBED_LABEL app_3.1_RC41"), "build_label_pattern": "app_{version}_RC{candidate}", "build_version_pattern": "{version}.{candidate}", "capture_groups": {"version": r"\d+\.\d+", "candidate": r"\d+"}, "short_version_string_pattern": "{version}"}, {"build_version": "3.1.41", "short_version_string": "3.1"})
	def test_build_label_substitution_multiline_input(self):
		self._assert_versiontool_result({"build_info_path": _str_io("\n".join(["FOO BAR", "BUILD_EMBED_LABEL app_3.1_RC41", "3 4"])), "build_label_pattern": "app_{version}_RC{candidate}", "build_version_pattern": "{version}.{candidate}", "capture_groups": {"version": r"\d+\.\d+", "candidate": r"\d+"}, "short_version_string_pattern": "{version}"}, {"build_version": "3.1.41", "short_version_string": "3.1"})
	def test_result_is_empty_if_label_is_missing_but_pattern_was_provided(self):
		self._assert_versiontool_result({"build_info_path": _str_io(), "build_label_pattern": "app_{version}_RC{candidate}", "build_version_pattern": "{version}.{candidate}", "capture_groups": {"version": r"\d+\.\d+", "candidate": r"\d+"}, "short_version_string_pattern": "{version}"}, {})
	def test_build_label_substitution_from_fallback_label(self):
		self._assert_versiontool_result({"build_info_path": _str_io("FOO 123"), "fallback_build_label": "app_99.99_RC99", "build_label_pattern": "app_{version}_RC{candidate}", "build_version_pattern": "{version}.{candidate}", "capture_groups": {"version": r"\d+\.\d+", "candidate": r"\d+"}, "short_version_string_pattern": "{version}"}, {"build_version": "99.99.99", "short_version_string": "99.99"})
	def test_build_label_substitution_uses_file_over_fallback_label(self):
		self._assert_versiontool_result({"build_info_path": _str_io("BUILD_EMBED_LABEL app_3.1_RC41"), "fallback_build_label": "app_99.99_RC99", "build_label_pattern": "app_{version}_RC{candidate}", "build_version_pattern": "{version}.{candidate}", "capture_groups": {"version": r"\d+\.\d+", "candidate": r"\d+"}, "short_version_string_pattern": "{version}"}, {"build_version": "3.1.41", "short_version_string": "3.1"})
	def test_raises_if_label_is_present_but_does_not_match(self):
		with self.assertRaises(versiontool.VersionToolError) as context:
			versiontool.VersionTool({"build_info_path": _str_io("BUILD_EMBED_LABEL app_3.1_RC41"), "build_label_pattern": "app_{version}_RC{candidate}", "build_version_pattern": "{version}.{candidate}", "capture_groups": {"version": r"\d+\.\d+\.\d+", "candidate": r"\d+"}, "short_version_string_pattern": "{version}"}).run()
	def test_raises_if_fallback_label_is_present_but_does_not_match(self):
		with self.assertRaises(versiontool.VersionToolError) as context:
			versiontool.VersionTool({"build_info_path": _str_io("FOO 123"), "fallback_build_label": "app_3.1_RC41", "build_label_pattern": "app_{version}_RC{candidate}", "build_version_pattern": "{version}.{candidate}", "capture_groups": {"version": r"\d+\.\d+\.\d+", "candidate": r"\d+"}, "short_version_string_pattern": "{version}"}).run()
if __name__ == "__main__":
	unittest.main()