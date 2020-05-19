"""facade - makes lightread_lib package easy to refactor
while keeping its api constant"""
from .helpers import set_up_logging
from .Window import Window
from .lightreadconfig import get_version