"""Build the Inception v3 network on ImageNet data set.
The Inception v3 architecture is described in http://arxiv.org/abs/1512.00567
Summary of available functions:
 inference: Compute inference on the model inputs to make a prediction
 loss: Compute the loss of the prediction with respect to the labels
"""
FLAGS = tf.app.flags.FLAGS
TOWER_NAME = "tower"
BATCHNORM_MOVING_AVERAGE_DECAY = 0.9997
MOVING_AVERAGE_DECAY = 0.9999
def inference(images, num_classes, for_training=False, restore_logits=True, scope=None):
	"""Build Inception v3 model architecture.
  See here for reference: http://arxiv.org/abs/1512.00567
  Args:
    images: Images returned from inputs() or distorted_inputs().
    num_classes: number of classes
    for_training: If set to `True`, build the inference model for training.
      Kernels that operate differently for inference during training
      e.g. dropout, are appropriately configured.
    restore_logits: whether or not the logits layers should be restored.
      Useful for fine-tuning a model with different num_classes.
    scope: optional prefix string identifying the ImageNet tower.
  Returns:
    Logits. 2-D float Tensor.
    Auxiliary Logits. 2-D float Tensor of side-head. Used for training only.
  """
	batch_norm_params = {"decay": BATCHNORM_MOVING_AVERAGE_DECAY, "epsilon": 0.001}
	with slim.arg_scope([slim.ops.conv2d, slim.ops.fc], weight_decay=0.00004):
		with slim.arg_scope([slim.ops.conv2d], stddev=0.1, activation=tf.nn.relu, batch_norm_params=batch_norm_params):
			logits, endpoints = slim.inception.inception_v3(images, dropout_keep_prob=0.8, num_classes=num_classes, is_training=for_training, restore_logits=restore_logits, scope=scope)
	_activation_summaries(endpoints)
	auxiliary_logits = endpoints["aux_logits"]
	return logits, auxiliary_logits
def loss(logits, labels, batch_size=None):
	"""Adds all losses for the model.
  Note the final loss is not returned. Instead, the list of losses are collected
  by slim.losses. The losses are accumulated in tower_loss() and summed to
  calculate the total loss.
  Args:
    logits: List of logits from inference(). Each entry is a 2-D float Tensor.
    labels: Labels from distorted_inputs or inputs(). 1-D tensor
            of shape [batch_size]
    batch_size: integer
  """
	if not batch_size:
		batch_size = FLAGS.batch_size
	sparse_labels = tf.reshape(labels, [batch_size, 1])
	indices = tf.reshape(tf.range(batch_size), [batch_size, 1])
	concated = tf.concat(axis=1, values=[indices, sparse_labels])
	num_classes = logits[0].get_shape()[-1].value
	dense_labels = tf.sparse_to_dense(concated, [batch_size, num_classes], 1.0, 0.0)
	slim.losses.cross_entropy_loss(logits[0], dense_labels, label_smoothing=0.1, weight=1.0)
	slim.losses.cross_entropy_loss(logits[1], dense_labels, label_smoothing=0.1, weight=0.4, scope="aux_loss")
def _activation_summary(x):
	"""Helper to create summaries for activations.
  Creates a summary that provides a histogram of activations.
  Creates a summary that measure the sparsity of activations.
  Args:
    x: Tensor
  """
	tensor_name = re.sub("%s_[0-9]*/" % TOWER_NAME, "", x.op.name)
	tf.summary.histogram(tensor_name + "/activations", x)
	tf.summary.scalar(tensor_name + "/sparsity", tf.nn.zero_fraction(x))
def _activation_summaries(endpoints):
	with tf.name_scope("summaries"):
		for act in endpoints.values():
			_activation_summary(act)