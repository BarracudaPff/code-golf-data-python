"""Tests for word2vec module."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
import tensorflow as tf
import word2vec
flags = tf.app.flags
FLAGS = flags.FLAGS
class Word2VecTest(tf.test.TestCase):
	def setUp(self):
		FLAGS.train_data = os.path.join(self.get_temp_dir(), "test-text.txt")
		FLAGS.eval_data = os.path.join(self.get_temp_dir(), "eval-text.txt")
		FLAGS.save_path = self.get_temp_dir()
		with open(FLAGS.train_data, "w") as f:
			f.write(
				"""alice was beginning to get very tired of sitting by her sister on
          the bank, and of having nothing to do: once or twice she had peeped
          into the book her sister was reading, but it had no pictures or
          conversations in it, 'and what is the use of a book,' thought alice
          'without pictures or conversations?' So she was considering in her own
          mind (as well as she could, for the hot day made her feel very sleepy
          and stupid), whether the pleasure of making a daisy-chain would be
          worth the trouble of getting up and picking the daisies, when suddenly
          a White rabbit with pink eyes ran close by her.\n"""
			)
			with open(FLAGS.eval_data, "w") as f:
				f.write("alice she rabbit once\n")
	def testWord2Vec(self):
		FLAGS.batch_size = 5
		FLAGS.num_neg_samples = 10
		FLAGS.epochs_to_train = 1
		FLAGS.min_count = 0
		word2vec.main([])
if __name__ == "__main__":
	tf.test.main()