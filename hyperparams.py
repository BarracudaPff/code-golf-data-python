"""
By kyubyong park. kbpark.linguist@gmail.com.
https://www.github.com/kyubyong/deepvoice3
"""
import math
def get_Ty(duration, sr, hop_length, r):
	"""Calculates number of paddings for reduction"""
	def _roundup(x):
		return math.ceil(x * 0.1) * 10
	T = _roundup(duration * sr / hop_length)
	num_paddings = r - (T % r) if T % r != 0 else 0
	T += num_paddings
	return T
class Hyperparams:
	"""Hyper parameters"""
	sr = 22050
	n_fft = 2048
	frame_shift = 0.0125
	frame_length = 0.05
	hop_length = int(sr * frame_shift)
	win_length = int(sr * frame_length)
	n_mels = 80
	sharpening_factor = 1.4
	n_iter = 50
	preemphasis = 0.97
	max_db = 100
	ref_db = 20
	r = 4
	dropout_rate = 0.2
	vocab_size = 32
	embed_size = 256
	enc_layers = 7
	enc_filter_size = 5
	enc_channels = 64
	dec_layers = 4
	dec_filter_size = 5
	attention_size = 128 * 2
	converter_layers = 5 * 2
	converter_filter_size = 5
	converter_channels = 256
	sinusoid = False
	attention_win_size = 3
	data = "LJSpeech-1.0"
	max_duration = 10.0
	Tx = 180
	Ty = int(get_Ty(max_duration, sr, hop_length, r))
	lr = 0.001
	logdir = "logdir"
	sampledir = "samples"
	batch_size = 16
	max_grad_norm = 100.0
	max_grad_val = 5.0
	num_iterations = 500000