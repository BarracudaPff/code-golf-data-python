import unittest
import Picture
import Pixel
import os.path
from java.awt import Color
from java.lang import ArrayIndexOutOfBoundsException
TEST_DIRECTORY = os.path.dirname(__file__) + "/"
PICTURES = TEST_DIRECTORY + "test-pictures/"
OUTPUT = TEST_DIRECTORY + "test-output/"
WHITE_BMP = PICTURES + "white.bmp"
WHITE_BMP_TITLE = WHITE_BMP
class Test_Picture_BMP(unittest.TestCase):
	def testPictureStrB1(self):
		"""Test Picture(String) constructor (bmp) [1] - loading"""
		self.pict = Picture()
		self.assertEqual(self.pict.load(WHITE_BMP), 1, "white.bmp could not be loaded")
	def testPictureStrB2(self):
		"""Test Picture(String) constructor (bmp) [2] - filename"""
		self.pict = Picture(WHITE_BMP)
		self.assertEqual(self.pict.getFileName(), WHITE_BMP, "Filename %s != %s" % (self.pict.getFileName(), WHITE_BMP))
	def testPictureStrB3(self):
		"""Test Picture(String) constructor (bmp) [3] - extension"""
		self.pict = Picture(WHITE_BMP)
		self.assertEqual(self.pict.getExtension(), "bmp", "File extension %s != bmp" % self.pict.getExtension())
	def testPictureStrB4(self):
		"""Test Picture(String) constructor (bmp) [4] - title"""
		self.pict = Picture(WHITE_BMP)
		self.assertEqual(self.pict.getTitle(), WHITE_BMP_TITLE, "Title %s != %s" % (self.pict.getTitle(), WHITE_BMP_TITLE))
	def testPictureStrB5(self):
		"""Test Picture(String) constructor (bmp) [5] - width"""
		self.pict = Picture(WHITE_BMP)
		self.assertEqual(self.pict.getWidth(), 50, "Width %s != 50" % self.pict.getWidth())
		self.assertNotEqual(self.pict.getWidth(), 49, "Width is 49?")
	def testPictureStrB6(self):
		"""Test Picture(String) constructor (bmp) [6] - height"""
		self.pict = Picture(WHITE_BMP)
		self.assertEqual(self.pict.getHeight(), 50, "Height %s != 50" % self.pict.getHeight())
	def testPictureStrB7(self):
		"""Test Picture(String) constructor (bmp) [7] - toString"""
		self.pict = Picture(WHITE_BMP)
		self.assertEqual(self.pict.toString(), "Picture, filename %s height 50 width 50" % WHITE_BMP, "toString %s != Picture, filename %s height 50 width 50" % (self.pict.toString(), WHITE_BMP))
	def testPictureStrB8(self):
		"""Test Picture(String) constructor (bmp) [8] - pixels"""
		self.pict = Picture(WHITE_BMP)
		self.height = self.pict.getHeight()
		self.width = self.pict.getWidth()
		if self.height != 50:
			print("Warning: height not correct")
		if self.width != 50:
			print("Warning: width not correct")
		for i in range(self.width):
			for j in range(self.height):
				self.pix = self.pict.getPixel(i, j)
				self.assertEqual(self.pix.getRed(), 255, "Pixel (%s,%s): Red = %s != 255" % (i, j, self.pix.getRed()))
				self.assertEqual(self.pix.getBlue(), 255, "Pixel (%s,%s): Blue = %s != 255" % (i, j, self.pix.getRed()))
				self.assertEqual(self.pix.getGreen(), 255, "Pixel (%s,%s): Green = %s != 255" % (i, j, self.pix.getRed()))
		self.pixarray = self.pict.getPixels()
		self.len = len(self.pixarray)
		self.assertEqual(self.len, 50 * 50, "Pixel array size %s != %s" % (self.len, 50 * 50))
		for k in range(self.len):
			self.pix = self.pixarray[k]
			self.assertEqual(self.pix.getRed(), 255, "Pixel (k:%s): Red = %s != 255" % (k, self.pix.getRed()))
			self.assertEqual(self.pix.getBlue(), 255, "Pixel (k:%s): Blue = %s != 255" % (k, self.pix.getBlue()))
			self.assertEqual(self.pix.getGreen(), 255, "Pixel (k:%s): Green = %s != 255" % (k, self.pix.getGreen()))
	def testPictureStrB(self):
		"""Test Picture(String) constructor (bmp) [all]"""
		self.pict = Picture(WHITE_BMP)
		self.assertEqual(self.pict.getFileName(), WHITE_BMP, "Filename %s != %s" % (self.pict.getFileName(), WHITE_BMP))
		self.assertEqual(self.pict.getExtension(), "bmp", "File extension %s != bmp" % self.pict.getExtension())
		self.assertEqual(self.pict.getTitle(), WHITE_BMP_TITLE, "Title %s != %s" % (self.pict.getTitle(), WHITE_BMP_TITLE))
		self.height = self.pict.getHeight()
		self.assertEqual(self.height, 50, "Height %s != 50" % self.height)
		self.width = self.pict.getWidth()
		self.assertEqual(self.width, 50, "Width %s != 50" % self.width)
		self.assertNotEqual(self.width, 49, "Width is 49?")
		self.assertEqual(self.pict.toString(), "Picture, filename %s height 50 width 50" % WHITE_BMP, "toString %s != Picture, filename %s height 50 width 50" % (self.pict.toString(), WHITE_BMP))
		for i in range(self.width):
			for j in range(self.height):
				self.pix = self.pict.getPixel(i, j)
				self.assertEqual(self.pix.getRed(), 255, "Pixel (%s,%s): Red = %s != 255" % (i, j, self.pix.getRed()))
				self.assertEqual(self.pix.getBlue(), 255, "Pixel (%s,%s): Blue = %s != 255" % (i, j, self.pix.getRed()))
				self.assertEqual(self.pix.getGreen(), 255, "Pixel (%s,%s): Green = %s != 255" % (i, j, self.pix.getRed()))
		self.pixarray = self.pict.getPixels()
		self.len = len(self.pixarray)
		self.assertEqual(self.len, 50 * 50, "Pixel array size %s != %s" % (self.len, 50 * 50))
		for k in range(self.len):
			self.pix = self.pixarray[k]
			self.assertEqual(self.pix.getRed(), 255, "Pixel (k:%s): Red = %s != 255" % (k, self.pix.getRed()))
			self.assertEqual(self.pix.getBlue(), 255, "Pixel (k:%s): Blue = %s != 255" % (k, self.pix.getBlue()))
			self.assertEqual(self.pix.getGreen(), 255, "Pixel (k:%s): Green = %s != 255" % (k, self.pix.getGreen()))
	def testPictureCopyB1(self):
		"""Test Picture(copyPicture) constructor (bmp) [1] - filename"""
		self.pict = Picture(WHITE_BMP)
		self.pict2 = Picture(self.pict)
		self.assertEqual(self.pict2.getFileName(), WHITE_BMP, "Filename %s != %s" % (self.pict2.getFileName(), WHITE_BMP))
	def testPictureCopyB2(self):
		"""Test Picture(copyPicture) constructor (bmp) [2] - extension"""
		self.pict = Picture(WHITE_BMP)
		self.pict2 = Picture(self.pict)
		self.assertEqual(self.pict2.getExtension(), "bmp", "File extension %s != bmp" % self.pict2.getExtension())
	def testPictureCopyB3(self):
		"""Test Picture(copyPicture) constructor (bmp) [3] - title"""
		self.pict = Picture(WHITE_BMP)
		self.pict2 = Picture(self.pict)
		self.assertEqual(self.pict2.getTitle(), WHITE_BMP_TITLE, "Title %s != %s" % (self.pict2.getTitle(), WHITE_BMP_TITLE))
	def testPictureCopyB4(self):
		"""Test Picture(copyPicture) constructor (bmp) [4] - width"""
		self.pict = Picture(WHITE_BMP)
		self.pict2 = Picture(self.pict)
		self.assertEqual(self.pict2.getWidth(), 50, "Width %s != 50" % self.pict2.getWidth())
	def testPictureCopyB5(self):
		"""Test Picture(copyPicture) constructor (bmp) [5] - height"""
		self.pict = Picture(WHITE_BMP)
		self.pict2 = Picture(self.pict)
		self.assertEqual(self.pict2.getHeight(), 50, "Height %s != 50" % self.pict2.getHeight())
	def testPictureCopyB6(self):
		"""Test Picture(copyPicture) constructor (bmp) [6] - width"""
		self.pict = Picture(WHITE_BMP)
		self.pict2 = Picture(self.pict)
		self.assertNotEqual(self.pict2.getWidth(), 49, "Width is 49?")
	def testPictureCopyB7(self):
		"""Test Picture(copyPicture) constructor (bmp) [7] - toString"""
		self.pict = Picture(WHITE_BMP)
		self.pict2 = Picture(self.pict)
		self.assertEqual(self.pict.toString(), "Picture, filename %s height 50 width 50" % WHITE_BMP, "toString %s != Picture, filename %s height 50 width 50" % (self.pict.toString(), WHITE_BMP))
	def testPictureCopyB8(self):
		"""Test Picture(copyPicture) constructor (bmp) [8] - pixels"""
		self.pict = Picture(WHITE_BMP)
		self.pict2 = Picture(self.pict)
		self.height = self.pict.getHeight()
		self.width = self.pict.getWidth()
		if self.height != 50:
			print("Warning: height not correct")
		if self.width != 50:
			print("Warning: width not correct")
		for i in range(self.width):
			for j in range(self.height):
				self.pix1 = self.pict.getPixel(i, j)
				self.pix2 = self.pict2.getPixel(i, j)
				self.assertEqual(self.pix1.getRed(), self.pix2.getRed(), "Pixel (%s,%s): Red = %s != %s" % (i, j, self.pix1.getRed(), self.pix2.getRed()))
				self.assertEqual(self.pix1.getBlue(), self.pix2.getBlue(), "Pixel (%s,%s): Blue = %s != %s" % (i, j, self.pix1.getBlue(), self.pix2.getBlue()))
				self.assertEqual(self.pix1.getGreen(), self.pix2.getGreen(), "Pixel (%s,%s): Green = %s != %s" % (i, j, self.pix1.getGreen(), self.pix2.getGreen()))
		self.pix1array = self.pict.getPixels()
		self.pix2array = self.pict2.getPixels()
		self.assertEqual(len(self.pix1array), len(self.pix2array), "Error, pixel arrays are different sizes")
		for k in range(len(self.pix1array)):
			self.pix1 = self.pix1array[k]
			self.pix2 = self.pix2array[k]
			self.assertEqual(self.pix1.getRed(), self.pix2.getRed(), "Pixel (k:%s): Red = %s != %s" % (k, self.pix1.getRed(), self.pix2.getRed()))
			self.assertEqual(self.pix1.getBlue(), self.pix2.getBlue(), "Pixel (k:%s): Blue = %s != %s" % (k, self.pix1.getBlue(), self.pix2.getBlue()))
			self.assertEqual(self.pix1.getGreen(), self.pix2.getGreen(), "Pixel (k:%s): Green = %s != %s" % (k, self.pix1.getGreen(), self.pix2.getGreen()))
	def testPictureCopyB(self):
		"""Test Picture(copyPicture) constructor (bmp) [all]"""
		self.pict = Picture(WHITE_BMP)
		self.pict2 = Picture(self.pict)
		self.assertEqual(self.pict2.getFileName(), WHITE_BMP, "Filename %s != %s" % (self.pict2.getFileName(), WHITE_BMP))
		self.assertEqual(self.pict2.getExtension(), "bmp", "File extension %s != bmp" % self.pict2.getExtension())
		self.assertEqual(self.pict2.getTitle(), WHITE_BMP_TITLE, "Title %s != %s" % (self.pict2.getTitle(), WHITE_BMP_TITLE))
		self.height = self.pict.getHeight()
		self.assertEqual(self.height, 50, "Height %s != 50" % self.height)
		self.width = self.pict.getWidth()
		self.assertEqual(self.width, 50, "Width %s != 50" % self.width)
		self.assertNotEqual(self.pict2.getWidth(), 49, "Width is 49?")
		self.assertEqual(self.pict.toString(), "Picture, filename %s height 50 width 50" % WHITE_BMP, "toString %s != Picture, filename %s height 50 width 50" % (self.pict.toString(), WHITE_BMP))
		for i in range(self.width):
			for j in range(self.height):
				self.pix1 = self.pict.getPixel(i, j)
				self.pix2 = self.pict2.getPixel(i, j)
				self.assertEqual(self.pix1.getRed(), self.pix2.getRed(), "Pixel (%s,%s): Red = %s != %s" % (i, j, self.pix1.getRed(), self.pix2.getRed()))
				self.assertEqual(self.pix1.getBlue(), self.pix2.getBlue(), "Pixel (%s,%s): Blue = %s != %s" % (i, j, self.pix1.getBlue(), self.pix2.getBlue()))
				self.assertEqual(self.pix1.getGreen(), self.pix2.getGreen(), "Pixel (%s,%s): Green = %s != %s" % (i, j, self.pix1.getGreen(), self.pix2.getGreen()))
		self.pix1array = self.pict.getPixels()
		self.pix2array = self.pict2.getPixels()
		self.assertEqual(len(self.pix1array), len(self.pix2array), "Error, pixel arrays are different sizes")
		for k in range(len(self.pix1array)):
			self.pix1 = self.pix1array[k]
			self.pix2 = self.pix2array[k]
			self.assertEqual(self.pix1.getRed(), self.pix2.getRed(), "Pixel (k:%s): Red = %s != %s" % (k, self.pix1.getRed(), self.pix2.getRed()))
			self.assertEqual(self.pix1.getBlue(), self.pix2.getBlue(), "Pixel (k:%s): Blue = %s != %s" % (k, self.pix1.getBlue(), self.pix2.getBlue()))
			self.assertEqual(self.pix1.getGreen(), self.pix2.getGreen(), "Pixel (k:%s): Green = %s != %s" % (k, self.pix1.getGreen(), self.pix2.getGreen()))
	def testTitlePsB(self):
		"""Test picture - changing title from Picture(String) (bmp)"""
		self.pict = Picture(WHITE_BMP)
		self.assertEqual(self.pict.getTitle(), WHITE_BMP_TITLE, "Title %s != %s" % (self.pict.getTitle(), WHITE_BMP_TITLE))
		self.pict.setTitle("Not white.bmp")
		self.assertNotEqual(self.pict.getTitle(), WHITE_BMP_TITLE, "Title is still white.bmp")
		self.assertEqual(self.pict.getTitle(), "Not white.bmp", "Title %s != Not white.bmp" % self.pict.getTitle())
	def testGetPictureWithHeightB1(self):
		"""Test Picture.getPictureWithHeight(int) (bmp) [1] - smaller"""
		self.pict = Picture()
		self.loaded = self.pict.load(PICTURES + "addMsg.bmp")
		self.assertEqual(self.loaded, 1, "Load is broken")
		self.heightSm = self.pict.getHeight() - 20
		self.pictSm1 = self.pict.getPictureWithHeight(self.heightSm)
		self.assertEqual(self.pictSm1.getHeight(), self.heightSm, "Height %s!=%s" % (self.pictSm1.getHeight(), self.heightSm))
		self.pictSm1.write(OUTPUT + "addMsgSmOut.bmp")
		self.pictSm2 = Picture()
		self.loaded = self.pictSm2.load(OUTPUT + "addMsgSmOut.bmp")
		self.assertEqual(self.loaded, 1, "Write seems to be broken")
		self.pictSm3 = Picture(PICTURES + "addMsgSm.bmp")
		self.assertEqual(self.pictSm2.getHeight(), self.heightSm, "Either write or load seems to be broken (Height %s != %s)" % (self.pictSm2.getHeight(), self.heightSm))
		self.assertEqual(self.pictSm2.getHeight(), self.pictSm3.getHeight(), "Height %s != %s" % (self.pictSm2.getHeight(), self.pictSm3.getHeight()))
		self.widthSm = self.pictSm1.getWidth()
		self.assertEqual(self.widthSm, self.pictSm2.getWidth(), "Width %s != %s" % (self.widthSm, self.pictSm2.getWidth()))
		self.assertEqual(self.pictSm2.getWidth(), self.pictSm3.getWidth(), "Width %s != %s" % (self.pictSm2.getWidth(), self.pictSm3.getWidth()))
		for i in range(self.widthSm):
			for j in range(self.heightSm):
				self.pix1 = self.pictSm2.getBasicPixel(i, j)
				self.pix2 = self.pictSm3.getBasicPixel(i, j)
				self.assertEqual(self.pix1, self.pix2, "Pixel (%s,%s): %s!=%s" % (i, j, self.pix1, self.pix2))
	def testGetPictureWithHeightB2(self):
		"""Test Picture.getPictureWithHeight(int) (bmp) [2] - larger"""
		self.pict = Picture()
		self.loaded = self.pict.load(PICTURES + "addMsg.bmp")
		self.assertEqual(self.loaded, 1, "Load is broken")
		self.heightLg = self.pict.getHeight() + 20
		self.pictLg1 = self.pict.getPictureWithHeight(self.heightLg)
		self.assertEqual(self.pictLg1.getHeight(), self.heightLg, "Height %s!=%s" % (self.pictLg1.getHeight(), self.heightLg))
		self.pictLg1.write(OUTPUT + "addMsgLgOut.bmp")
		self.pictLg2 = Picture()
		self.loaded = self.pictLg2.load(OUTPUT + "addMsgLgOut.bmp")
		self.assertEqual(self.loaded, 1, "Write seems to be broken")
		self.pictLg3 = Picture(PICTURES + "addMsgLg.bmp")
		self.assertEqual(self.pictLg2.getHeight(), self.heightLg, "Either write or load seems to be broken (Height %s != %s)" % (self.pictLg2.getHeight(), self.heightLg))
		self.assertEqual(self.pictLg2.getHeight(), self.pictLg3.getHeight(), "Height %s != %s" % (self.pictLg2.getHeight(), self.pictLg3.getHeight()))
		self.widthLg = self.pictLg1.getWidth()
		self.assertEqual(self.widthLg, self.pictLg2.getWidth(), "Width %s != %s" % (self.widthLg, self.pictLg2.getWidth()))
		self.assertEqual(self.pictLg2.getWidth(), self.pictLg3.getWidth(), "Width %s != %s" % (self.pictLg2.getWidth(), self.pictLg3.getWidth()))
		for i in range(self.widthLg):
			for j in range(self.heightLg):
				self.pix1 = self.pictLg2.getBasicPixel(i, j)
				self.pix2 = self.pictLg3.getBasicPixel(i, j)
				self.assertEqual(self.pix1, self.pix2, "Pixel (%s,%s): %s!=%s" % (i, j, self.pix1, self.pix2))
	def testWriteB(self):
		"""Test Picture.write (bmp)"""
		self.pict1 = Picture()
		self.assertEqual(self.pict1.load(WHITE_BMP), 1, "white.bmp could not be loaded, so write will not be tested")
		self.pict2 = Picture(WHITE_BMP)
		self.pict2.write(OUTPUT + "writeTest.bmp")
		self.pict3 = Picture(OUTPUT + "writeTest.bmp")
		self.height = self.pict3.getHeight()
		self.assertEqual(self.height, 50, "Height %s != 50" % self.height)
		self.width = self.pict3.getWidth()
		self.assertEqual(self.width, 50, "Width %s != 50" % self.width)
		for i in range(self.width):
			for j in range(self.height):
				self.pix1 = self.pict2.getBasicPixel(i, j)
				self.pix2 = self.pict3.getBasicPixel(i, j)
				self.assertEqual(self.pix1, self.pix2, "Pixel (%s,%s): %s!=%s" % (i, j, self.pix1, self.pix2))