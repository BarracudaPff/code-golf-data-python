from unittest import TestCase
from pippi import tune
class TestChords(TestCase):
	def test_get_quality(self):
		assert tune.get_quality("ii") == "-"
		assert tune.get_quality("II") == "^"
		assert tune.get_quality("vi69") == "-"
		assert tune.get_quality("vi6/9") == "-"
		assert tune.get_quality("ii7") == "-"
		assert tune.get_quality("v*9") == "*"
	def test_get_extension(self):
		assert tune.get_extension("ii") == ""
		assert tune.get_extension("II") == ""
		assert tune.get_extension("vi69") == "69"
		assert tune.get_extension("vi6/9") == "69"
		assert tune.get_extension("ii7") == "7"
		assert tune.get_extension("v*9") == "9"
	def test_get_intervals(self):
		assert tune.get_intervals("ii") == ["P1", "m3", "P5"]
		assert tune.get_intervals("II") == ["P1", "M3", "P5"]
		assert tune.get_intervals("II7") == ["P1", "M3", "P5", "m7"]
		assert tune.get_intervals("v6/9") == ["P1", "m3", "P5", "M6", "M9"]
	def test_add_intervals(self):
		assert tune.add_intervals("P5", "P8") == "P12"
		assert tune.add_intervals("m3", "P8") == "m10"
		assert tune.add_intervals("m3", "m3") == "TT"
		assert tune.add_intervals("m3", "M3") == "P5"
	def test_get_chord(self):
		assert tune.chord("I7", key="a", octave=4, ratios=tune.just) == [440.0, 550.0, 660.0, 792.0]
		assert tune.chord("I7", key="a", octave=3, ratios=tune.just) == [220.0, 275.0, 330.0, 396.0]
	def test_get_ratio_from_interval(self):
		assert tune.get_ratio_from_interval("P1", tune.just) == 1.0
		assert tune.get_ratio_from_interval("P5", tune.just) == 1.5
		assert tune.get_ratio_from_interval("P8", tune.just) == 2.0
		assert tune.get_ratio_from_interval("m10", tune.just) == 2.4
		assert tune.get_ratio_from_interval("P15", tune.just) == 4.0