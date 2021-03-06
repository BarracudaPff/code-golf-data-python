"""Helper functions used in both train and inference."""
def GetConfigString(config_file):
	config_string = ""
	if config_file is not None:
		config_string = open(config_file).read()
	return config_string
class InputConfig(object):
	def __init__(self, config_string):
		config = json.loads(config_string)
		self.data = config["data"]
		self.unique_code_size = config["unique_code_size"]
class TrainConfig(object):
	def __init__(self, config_string):
		config = json.loads(config_string)
		self.batch_size = config["batch_size"]
		self.learning_rate = config["learning_rate"]
		self.decay_rate = config["decay_rate"]
		self.samples_per_decay = config["samples_per_decay"]
def SaveConfig(directory, filename, config_string):
	path = os.path.join(directory, filename)
	with tf.gfile.Open(path, mode="w") as f:
		f.write(config_string)