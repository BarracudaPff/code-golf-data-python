"""Tests for domain_adaptation.pixel_domain_adaptation.pixelda_preprocess."""
class PixelDAPreprocessTest(tf.test.TestCase):
	def assert_preprocess_classification_is_centered(self, dtype, is_training):
		tf.set_random_seed(0)
		if dtype == tf.uint8:
			image = tf.random_uniform((100, 200, 3), maxval=255, dtype=tf.int64)
			image = tf.cast(image, tf.uint8)
		else:
			image = tf.random_uniform((100, 200, 3), maxval=1.0, dtype=dtype)
		labels = {}
		image, labels = pixelda_preprocess.preprocess_classification(image, labels, is_training=is_training)
		with self.test_session() as sess:
			np_image = sess.run(image)
			self.assertTrue(np_image.min() <= -0.95)
			self.assertTrue(np_image.min() >= -1.0)
			self.assertTrue(np_image.max() >= 0.95)
			self.assertTrue(np_image.max() <= 1.0)
	def testPreprocessClassificationZeroCentersUint8DuringTrain(self):
		self.assert_preprocess_classification_is_centered(tf.uint8, is_training=True)
	def testPreprocessClassificationZeroCentersUint8DuringTest(self):
		self.assert_preprocess_classification_is_centered(tf.uint8, is_training=False)
	def testPreprocessClassificationZeroCentersFloatDuringTrain(self):
		self.assert_preprocess_classification_is_centered(tf.float32, is_training=True)
	def testPreprocessClassificationZeroCentersFloatDuringTest(self):
		self.assert_preprocess_classification_is_centered(tf.float32, is_training=False)
if __name__ == "__main__":
	tf.test.main()