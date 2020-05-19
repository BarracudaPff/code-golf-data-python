"""Evaluates a TFGAN trained compression model."""
flags = tf.flags
FLAGS = flags.FLAGS
flags.DEFINE_string("master", "", "Name of the TensorFlow master to use.")
flags.DEFINE_string("checkpoint_dir", "/tmp/compression/", "Directory where the model was written to.")
flags.DEFINE_string("eval_dir", "/tmp/compression/", "Directory where the results are saved to.")
flags.DEFINE_integer("max_number_of_evaluations", None, "Number of times to run evaluation. If `None`, run " "forever.")
flags.DEFINE_string("dataset_dir", None, "Location of data.")
flags.DEFINE_integer("batch_size", 32, "The number of images in each batch.")
flags.DEFINE_integer("patch_size", 32, "The size of the patches to train on.")
flags.DEFINE_integer("bits_per_patch", 1230, "The number of bits to produce per patch.")
flags.DEFINE_integer("model_depth", 64, "Number of filters for compression model")
def main(_, run_eval_loop=True):
	with tf.name_scope("inputs"):
		images = data_provider.provide_data("validation", FLAGS.batch_size, dataset_dir=FLAGS.dataset_dir, patch_size=FLAGS.patch_size)
	with tf.variable_scope("generator"):
		reconstructions, _, prebinary = networks.compression_model(images, num_bits=FLAGS.bits_per_patch, depth=FLAGS.model_depth, is_training=False)
	summaries.add_reconstruction_summaries(images, reconstructions, prebinary)
	pixel_loss_per_example = tf.reduce_mean(tf.abs(images - reconstructions), axis=[1, 2, 3])
	pixel_loss = tf.reduce_mean(pixel_loss_per_example)
	tf.summary.histogram("pixel_l1_loss_hist", pixel_loss_per_example)
	tf.summary.scalar("pixel_l1_loss", pixel_loss)
	uint8_images = data_provider.float_image_to_uint8(images)
	uint8_reconstructions = data_provider.float_image_to_uint8(reconstructions)
	uint8_reshaped = summaries.stack_images(uint8_images, uint8_reconstructions)
	image_write_ops = tf.write_file("%s/%s" % (FLAGS.eval_dir, "compression.png"), tf.image.encode_png(uint8_reshaped[0]))
	if not run_eval_loop:
		return
	tf.contrib.training.evaluate_repeatedly(FLAGS.checkpoint_dir, master=FLAGS.master, hooks=[tf.contrib.training.SummaryAtEndHook(FLAGS.eval_dir), tf.contrib.training.StopAfterNEvalsHook(1)], eval_ops=image_write_ops, max_number_of_evaluations=FLAGS.max_number_of_evaluations)
if __name__ == "__main__":
	tf.app.run()