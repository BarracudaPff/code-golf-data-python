import os
import os.path
import unittest
from media import *
import java.awt.Color
TEST_DIRECTORY = os.path.dirname(__file__) + "/"
class Test_Pixel(unittest.TestCase):
	def setUp(self):
		setTestMediaFolder()
		self.consts = {"XVAL": 2, "YVAL": 2, "RED": 0xFF0000, "GREEN": 0xFF00, "BLUE": 0xFF, "1RED": 212, "1BLUE": 100, "1GREEN": 40, "1ALPHA": 142, "MAXRGB": 255, "PICNAME": TEST_DIRECTORY + "test-pictures/9by9.bmp", "TMPFILE": TEST_DIRECTORY + "test-output/9by9-tmp.bmp"}
		self.pic1 = Picture()
		self.pic1.loadImage(self.consts["PICNAME"])
		self.pix1 = getPixel(self.pic1, self.consts["XVAL"], self.consts["YVAL"])
	def testConstruct(self):
		self.assertEqual(getX(self.pix1), self.consts["XVAL"], "Pixel values not set properly in Pixel Constructor.")
		self.assertEqual(getY(self.pix1), self.consts["YVAL"], "Pixel values not set properly in Pixel Constructor.")
		self.assertEqual(self.pix1.getX(), self.consts["XVAL"], "Pixel values not set properly in Pixel Constructor.")
		self.assertEqual(self.pix1.getY(), self.consts["YVAL"], "Pixel values not set properly in Pixel Constructor.")
	def testGetSetRed(self):
		setRed(self.pix1, self.consts["1RED"])
		self.assertEqual(self.consts["1RED"], getRed(self.pix1), "Pixel did not modify red value properly.")
	def testGetSetGreen(self):
		setGreen(self.pix1, self.consts["1GREEN"])
		self.assertEqual(self.consts["1GREEN"], getGreen(self.pix1), "Pixel did not modify green value properly.")
	def testGetSetBlue(self):
		setBlue(self.pix1, self.consts["1BLUE"])
		self.assertEqual(self.consts["1BLUE"], getBlue(self.pix1), "Pixel did not modify blue value properly.")
	def testOverUnderSet(self):
		setRed(self.pix1, 400)
		setBlue(self.pix1, -10)
		self.assertEqual(self.consts["MAXRGB"], getRed(self.pix1), "Pixel did not handle too high setColor value")
		self.assertEqual(0, getBlue(self.pix1), "Pixel did not handle -negative setcolor value.")
	def testWhiteBlack(self):
		self.pix1 = getPixel(self.pic1, 0, 0)
		self.assertEqual(self.consts["MAXRGB"], getRed(self.pix1), "Pixel did not handle red 255 in a white pixel")
		self.assertEqual(self.consts["MAXRGB"], getGreen(self.pix1), "Pixel did not handle green 255 in a white pixel.")
		self.assertEqual(self.consts["MAXRGB"], getBlue(self.pix1), "Pixel did not handle blue 255 in a white pixel.")
		self.pix2 = getPixel(self.pic1, 2, 2)
		self.assertEqual(0, getRed(self.pix2), "Pixel did not handle 0 Red val in a black pixel.")
		self.assertEqual(0, getGreen(self.pix2), "Pixel did not handle 0 Green value in a black pixel.")
		self.assertEqual(0, getBlue(self.pix2), "Pixel did not handle 0 Blue value in a black pixel.")
	def testGetSetColor(self):
		color1 = Color(self.consts["1RED"], self.consts["1GREEN"], self.consts["1BLUE"])
		setColor(self.pix1, color1)
		color2 = getColor(self.pix1)
		self.assert_(color1 == color2, "Pixel did not setColor correctly.")
	def testPixWrite(self):
		color1 = Color(self.consts["1RED"], self.consts["1GREEN"], self.consts["1BLUE"])
		setColor(self.pix1, color1)
		writePictureTo(self.pic1, self.consts["TMPFILE"])
		self.pic2 = Picture()
		self.pic2.loadImage(self.consts["TMPFILE"])
		self.pix2 = getPixel(self.pic2, self.consts["XVAL"], self.consts["YVAL"])
		os.remove(self.consts["TMPFILE"])
		self.assert_(getColor(self.pix1) == getColor(self.pix2), "Pixel change did not properly save to file.  You may need to delete %s from the working directory." % (self.consts["TMPFILE"]))