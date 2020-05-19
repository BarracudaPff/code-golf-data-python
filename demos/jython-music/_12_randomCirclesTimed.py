from gui import *
from random import *
from music import *
delay = 500
d = Display("Random Timed Circles with Sound")
def drawCircle():
	"""Draws one random circle and plays the corresponding note."""
	global d
	x = randint(0, d.getWidth())
	y = randint(0, d.getHeight())
	radius = randint(5, 40)
	red = randint(100, 255)
	blue = randint(0, 100)
	color = Color(red, 0, blue)
	c = Circle(x, y, radius, color, True)
	d.add(c)
	pitch = mapScale(255 - red + blue, 0, 255, C4, C6, MAJOR_SCALE)
	dynamic = mapValue(radius, 5, 40, 20, 127)
	Play.note(pitch, 0, 5000, dynamic)
t = Timer(delay, drawCircle)
title = "Delay"
xPosition = d.getWidth() / 3
yPosition = d.getHeight() + 45
d1 = Display(title, 250, 50, xPosition, yPosition)
def timerSet(value):
	global t, d1, title
	t.setDelay(value)
	d1.setTitle(title + " (" + str(value) + " msec)")
s1 = Slider(HORIZONTAL, 10, delay * 2, delay, timerSet)
d1.add(s1, 25, 10)
t.start()