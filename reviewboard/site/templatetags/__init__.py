from __future__ import unicode_literals
try:
	from django.template.base import add_to_builtins
	add_to_builtins(__name__ + ".localsite")
except ImportError:
	pass