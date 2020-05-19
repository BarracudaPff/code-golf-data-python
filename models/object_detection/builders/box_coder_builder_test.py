"""Tests for box_coder_builder."""
class BoxCoderBuilderTest(tf.test.TestCase):
	def test_build_faster_rcnn_box_coder_with_defaults(self):
		box_coder_text_proto = """
      faster_rcnn_box_coder {
      }
    """
		box_coder_proto = box_coder_pb2.BoxCoder()
		text_format.Merge(box_coder_text_proto, box_coder_proto)
		box_coder_object = box_coder_builder.build(box_coder_proto)
		self.assertIsInstance(box_coder_object, faster_rcnn_box_coder.FasterRcnnBoxCoder)
		self.assertEqual(box_coder_object._scale_factors, [10.0, 10.0, 5.0, 5.0])
	def test_build_faster_rcnn_box_coder_with_non_default_parameters(self):
		box_coder_text_proto = """
      faster_rcnn_box_coder {
        y_scale: 6.0
        x_scale: 3.0
        height_scale: 7.0
        width_scale: 8.0
      }
    """
		box_coder_proto = box_coder_pb2.BoxCoder()
		text_format.Merge(box_coder_text_proto, box_coder_proto)
		box_coder_object = box_coder_builder.build(box_coder_proto)
		self.assertIsInstance(box_coder_object, faster_rcnn_box_coder.FasterRcnnBoxCoder)
		self.assertEqual(box_coder_object._scale_factors, [6.0, 3.0, 7.0, 8.0])
	def test_build_keypoint_box_coder_with_defaults(self):
		box_coder_text_proto = """
      keypoint_box_coder {
      }
    """
		box_coder_proto = box_coder_pb2.BoxCoder()
		text_format.Merge(box_coder_text_proto, box_coder_proto)
		box_coder_object = box_coder_builder.build(box_coder_proto)
		self.assertIsInstance(box_coder_object, keypoint_box_coder.KeypointBoxCoder)
		self.assertEqual(box_coder_object._scale_factors, [10.0, 10.0, 5.0, 5.0])
	def test_build_keypoint_box_coder_with_non_default_parameters(self):
		box_coder_text_proto = """
      keypoint_box_coder {
        num_keypoints: 6
        y_scale: 6.0
        x_scale: 3.0
        height_scale: 7.0
        width_scale: 8.0
      }
    """
		box_coder_proto = box_coder_pb2.BoxCoder()
		text_format.Merge(box_coder_text_proto, box_coder_proto)
		box_coder_object = box_coder_builder.build(box_coder_proto)
		self.assertIsInstance(box_coder_object, keypoint_box_coder.KeypointBoxCoder)
		self.assertEqual(box_coder_object._num_keypoints, 6)
		self.assertEqual(box_coder_object._scale_factors, [6.0, 3.0, 7.0, 8.0])
	def test_build_mean_stddev_box_coder(self):
		box_coder_text_proto = """
      mean_stddev_box_coder {
      }
    """
		box_coder_proto = box_coder_pb2.BoxCoder()
		text_format.Merge(box_coder_text_proto, box_coder_proto)
		box_coder_object = box_coder_builder.build(box_coder_proto)
		self.assertTrue(isinstance(box_coder_object, mean_stddev_box_coder.MeanStddevBoxCoder))
	def test_build_square_box_coder_with_defaults(self):
		box_coder_text_proto = """
      square_box_coder {
      }
    """
		box_coder_proto = box_coder_pb2.BoxCoder()
		text_format.Merge(box_coder_text_proto, box_coder_proto)
		box_coder_object = box_coder_builder.build(box_coder_proto)
		self.assertTrue(isinstance(box_coder_object, square_box_coder.SquareBoxCoder))
		self.assertEqual(box_coder_object._scale_factors, [10.0, 10.0, 5.0])
	def test_build_square_box_coder_with_non_default_parameters(self):
		box_coder_text_proto = """
      square_box_coder {
        y_scale: 6.0
        x_scale: 3.0
        length_scale: 7.0
      }
    """
		box_coder_proto = box_coder_pb2.BoxCoder()
		text_format.Merge(box_coder_text_proto, box_coder_proto)
		box_coder_object = box_coder_builder.build(box_coder_proto)
		self.assertTrue(isinstance(box_coder_object, square_box_coder.SquareBoxCoder))
		self.assertEqual(box_coder_object._scale_factors, [6.0, 3.0, 7.0])
	def test_raise_error_on_empty_box_coder(self):
		box_coder_text_proto = """
    """
		box_coder_proto = box_coder_pb2.BoxCoder()
		text_format.Merge(box_coder_text_proto, box_coder_proto)
		with self.assertRaises(ValueError):
			box_coder_builder.build(box_coder_proto)
if __name__ == "__main__":
	tf.test.main()