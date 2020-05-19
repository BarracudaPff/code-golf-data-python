from __future__ import absolute_import, unicode_literals
from unittest import skipIf, TestCase
import six
if six.PY3:
	TestCase.assertItemsEqual = TestCase.assertCountEqual