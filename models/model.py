import math
import time
import os
import numpy as np
from keras.engine.training import GeneratorEnqueuer
from tools.save_images import save_img3
from keras import backend as K
def channel_idx():
	if K.image_dim_ordering() == "th":
		return 1
	else:
		return 3
class Model:
	"""
    Interface for normal (one net) models and adversarial models. Objects of
    classes derived from Model are returned by method make() of the
    Model_Factory class.
    """
	def train(self, train_gen, valid_gen, cb):
		pass
	def train2(self, load_data_func, cb):
		pass
	def predict(self, test_gen, tag="pred"):
		pass
	def test(self, test_gen):
		pass
class One_Net_Model(Model):
	"""
    Wraper of regular models like FCN, SegNet etc consisting of a one Keras
    model. But not GANs, which are made of two networks and have a different
    training strategy. In this class we implement the train(), test() and
    predict() methods common to all of them.
    """
	def __init__(self, model, cf, optimizer):
		self.cf = cf
		self.optimizer = optimizer
		self.model = model
	def train(self, train_gen, valid_gen, cb):
		if self.cf.train_model:
			print("\n > Training the model...")
			hist = self.model.fit_generator(generator=train_gen, samples_per_epoch=self.cf.dataset.n_images_train, nb_epoch=self.cf.n_epochs, verbose=1, callbacks=cb, validation_data=valid_gen, nb_val_samples=self.cf.dataset.n_images_valid, class_weight=None, max_q_size=self.cf.max_q_size, nb_worker=self.cf.workers, pickle_safe=True)
			print("   Training finished.")
			return hist
		else:
			return None
	def train2(self, load_data_func, cb):
		if self.cf.train_model:
			print("\n > Training the model...")
			(x_train, y_train), (x_test, y_test) = load_data_func(os.path.join(self.cf.dataset.path, self.cf.dataset.dataset_name + ".pkl.gz"))
			img_rows, img_cols = self.cf.dataset.img_shape
			if K.image_dim_ordering() == "th":
				x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
				x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
			elif K.image_dim_ordering() == "tf":
				x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
				x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
			x_train = x_train.astype("float32")
			x_test = x_test.astype("float32")
			x_train /= 255
			x_test /= 255
			y_train2 = np.zeros((len(y_train), self.cf.dataset.n_classes), dtype="float32")
			for i, label in enumerate(y_train):
				y_train2[i, label] = 1.0
			y_train = y_train2
			hist = self.model.fit(x=x_train, y=y_train, batch_size=self.cf.batch_size_train, validation_split=0.2, nb_epoch=self.cf.n_epochs, verbose=1, callbacks=cb, class_weight=None)
			print("   Training finished.")
			return hist
		else:
			return None
	def predict(self, test_gen, tag="pred"):
		if self.cf.pred_model:
			print("\n > Predicting the model...")
			self.model.load_weights(self.cf.weights_file)
			data_gen_queue, _stop, _generator_threads = GeneratorEnqueuer(self.test_gen, max_q_size=cf.max_q_size)
			start_time = time.time()
			for _ in range(int(math.ceil(self.cf.dataset.n_images_train / float(self.cf.batch_size_test)))):
				data = data_gen_queue.get()
				x_true = data[0]
				y_true = data[1].astype("int32")
				y_pred = self.model.predict(x_true)
				y_pred = np.argmax(y_pred, axis=1)
				y_true = np.reshape(y_true, (y_true.shape[0], y_true.shape[2], y_true.shape[3]))
				save_img3(x_true, y_true, y_pred, self.cf.savepath, 0, self.cf.dataset.color_map, self.cf.dataset.classes, tag + str(_), self.cf.dataset.void_class)
			_stop.set()
			total_time = time.time() - start_time
			fps = float(self.cf.dataset.n_images_test) / total_time
			s_p_f = total_time / float(self.cf.dataset.n_images_test)
			print("   Predicting time: {}. FPS: {}. Seconds per Frame: {}".format(total_time, fps, s_p_f))
	def test(self, test_gen):
		if self.cf.test_model:
			print("\n > Testing the model...")
			self.model.load_weights(self.cf.weights_file)
			start_time = time.time()
			test_metrics = self.model.evaluate_generator(test_gen, self.cf.dataset.n_images_test, max_q_size=self.cf.max_q_size, nb_worker=self.cf.workers, pickle_safe=True)
			total_time = time.time() - start_time
			fps = float(self.cf.dataset.n_images_test) / total_time
			s_p_f = total_time / float(self.cf.dataset.n_images_test)
			print("   Testing time: {}. FPS: {}. Seconds per Frame: {}".format(total_time, fps, s_p_f))
			if self.cf.problem_type == "detection":
				raise ValueError("Copy from master repository")
			elif self.cf.problem_type == "segmentation":
				metrics_dict = dict(zip(self.model.metrics_names, test_metrics))
				I = np.zeros(self.cf.dataset.n_classes)
				U = np.zeros(self.cf.dataset.n_classes)
				jacc_percl = np.zeros(self.cf.dataset.n_classes)
				for i in range(self.cf.dataset.n_classes):
					I[i] = metrics_dict["I" + str(i)]
					U[i] = metrics_dict["U" + str(i)]
					jacc_percl[i] = I[i] / U[i]
					print("   {:2d} ({:^15}): Jacc: {:6.2f}".format(i, self.cf.dataset.classes[i], jacc_percl[i] * 100))
				jacc_mean = np.nanmean(jacc_percl)
				print("   Jaccard mean: {}".format(jacc_mean))