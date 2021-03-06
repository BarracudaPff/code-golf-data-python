from __future__ import absolute_import, division, print_function, unicode_literals
from ..registry_tools import iso_register
from .core import UnitedStates
@iso_register("US-OK")
class Oklahoma(UnitedStates):
	"""Oklahoma"""
	include_thanksgiving_friday = True
	include_boxing_day = True
	include_columbus_day = False