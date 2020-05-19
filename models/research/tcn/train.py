"""Trains TCN models (and baseline comparisons)."""
tf.logging.set_verbosity(tf.logging.INFO)
tf.flags.DEFINE_string(
	"config_paths",
	"",
	"""
    Path to a YAML configuration files defining FLAG values. Multiple files
    can be separated by the `#` symbol. Files are merged recursively. Setting
    a key in these files is equivalent to setting the FLAG value with
    the same name.
    """,
)
tf.flags.DEFINE_string("model_params", "{}", "YAML configuration string for the model parameters.")
tf.app.flags.DEFINE_string("master", "local", "BNS name of the TensorFlow master to use")
tf.app.flags.DEFINE_string("logdir", "/tmp/tcn", "Directory where to write event logs.")
tf.app.flags.DEFINE_integer("task", 0, "Task id of the replica running the training.")
tf.app.flags.DEFINE_integer("ps_tasks", 0, "Number of tasks in the ps job. If 0 no ps job is used.")
FLAGS = tf.app.flags.FLAGS
def main(_):
	"""Runs main training loop."""
	config = util.ParseConfigsToLuaTable(FLAGS.config_paths, FLAGS.model_params, save=True, logdir=FLAGS.logdir)
	estimator = get_estimator(config, FLAGS.logdir)
	estimator.train()
if __name__ == "__main__":
	tf.app.run()