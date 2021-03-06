"""Module for training.
"""
import logging
import pprint
import sys
import time
import numpy as np
from . import exp, viz
from .utils import convert_to_numpy, update_dict_of_lists
from .viz import plot
__author__ = "R Devon Hjelm"
__author_email__ = "erroneus@gmail.com"
logger = logging.getLogger("cortex.train")
def summarize_results(results):
	results_ = {}
	for k, v in results.items():
		if isinstance(v, dict):
			results_[k] = summarize_results(v)
		else:
			if len(v) > 0:
				try:
					results_[k] = np.mean(v)
				except BaseException:
					raise ValueError("Something is wrong with result {} of type {}.".format(k, type(v[0])))
	return results_
def summarize_results_std(results):
	results_ = {}
	for k, v in results.items():
		if isinstance(v, dict):
			results_[k] = summarize_results(v)
		else:
			results_[k] = np.std(v)
	return results_
def train_epoch(model, epoch, eval_during_train, data_mode="train", use_pbar=True):
	model.train_loop(epoch, data_mode=data_mode, use_pbar=use_pbar)
	if not eval_during_train:
		return test_epoch(model, epoch, data_mode=data_mode, use_pbar=use_pbar)
	results = summarize_results(model._all_epoch_results)
	return results
def test_epoch(model, epoch, data_mode="test", use_pbar=True):
	model.eval_loop(epoch, data_mode=data_mode, use_pbar=use_pbar)
	results = summarize_results(model._all_epoch_results)
	model.data.reset(make_pbar=False, mode="test")
	model.data.next()
	model.visualize(auto_input=True)
	return results
def display_results(train_results, test_results, epoch, epochs, epoch_time, total_time):
	if epochs and epoch:
		print("\n\tEpoch {}/{} took {:.3f}s. Total time: {:.2f}".format(epoch + 1, epochs, epoch_time, total_time))
	times = train_results.pop("times", None)
	if times:
		time_strs = ["{}: {:.2f}".format(k, v) for k, v in times.items()]
		print("\tAvg update times: " + " | ".join(time_strs))
	train_losses = train_results.pop("losses")
	test_losses = test_results.pop("losses")
	loss_strs = ["{}: {:.2f} / {:.2f}".format(k, train_losses[k], test_losses[k]) for k in train_losses.keys()]
	print("\tAvg loss: " + " | ".join(loss_strs))
	for k in train_results.keys():
		v_train = train_results[k]
		v_test = test_results[k] if k in test_results else None
		if v_test is None:
			if isinstance(v_train, dict):
				print("\t" + k + ": " + " | ".join(["{}: {:.2f}".format(k_, v_train[k_]) for k_ in v_train.keys()]))
			else:
				print("\t{}: {:.2f}".format(k, v_train))
		else:
			if isinstance(v_train, dict):
				print("\t" + k + ": " + " | ".join(["{}: {:.2f} / {:.2f}".format(k_, v_train[k_], v_test[k_]) for k_ in v_train.keys()]))
			else:
				print("\t{}: {:.2f} / {:.2f}".format(k, v_train, v_test))
def align_summaries(d_train, d_test):
	keys = set(d_train.keys()).union(set(d_test.keys()))
	for k in keys:
		if k in d_train and k in d_test:
			v_train = d_train[k]
			v_test = d_test[k]
			if isinstance(v_train, dict):
				max_train_len = max([len(v) for v in v_train.values()])
				max_test_len = max([len(v) for v in v_test.values()])
				max_len = max(max_train_len, max_test_len)
				for k_, v in v_train.items():
					if len(v) < max_len:
						v_train[k_] = v_train[k_] + [v_train[k_][-1]] * (max_len - len(v_train[k_]))
				for k_, v in v_test.items():
					if len(v) < max_len:
						v_test[k_] = v_test[k_] + [v_test[k_][-1]] * (max_len - len(v_test[k_]))
			else:
				if len(v_train) > len(v_test):
					d_test[k] = v_test + [v_test[-1]] * (len(v_train) - len(v_test))
				elif len(v_test) > len(v_train):
					d_train[k] = v_train + [v_train[-1]] * (len(v_test) - len(v_train))
		elif k in d_train:
			v_train = d_train[k]
			if isinstance(v_train, dict):
				max_len = max([len(v) for v in v_train.values()])
				for k_, v in v_train.items():
					if len(v) < max_len:
						v_train[k_] = v_train[k_] + [v_train[k_][-1]] * (max_len - len(v_train[k_]))
		elif k in d_test:
			v_test = d_test[k]
			if isinstance(v_test, dict):
				max_len = max([len(v) for v in v_test.values()])
				for k_, v in v_test.items():
					if len(v) < max_len:
						v_test[k_] = v_test[k_] + [v_test[k_][-1]] * (max_len - len(v_test[k_]))
def save_best(model, train_results, best, save_on_best, save_on_lowest):
	flattened_results = {}
	for k, v in train_results.items():
		if isinstance(v, dict):
			for k_, v_ in v.items():
				flattened_results[k + "." + k_] = v_
		else:
			flattened_results[k] = v
	if save_on_best in flattened_results:
		current = flattened_results[save_on_best]
		if not best:
			found_best = True
		elif save_on_lowest:
			found_best = current < best
		else:
			found_best = current > best
		if found_best:
			best = current
			print("\nFound best {} (train): {}".format(save_on_best, best))
			exp.save(model, prefix="best_" + save_on_best)
		return best
def main_loop(model, epochs=500, archive_every=10, save_on_best=None, save_on_lowest=None, save_on_highest=None, eval_during_train=True, train_mode="train", test_mode="test", eval_only=False, pbar_off=False):
	"""
    Args:
        epochs: Number of epochs.
        archive_every: Number of epochs for writing checkpoints.
        save_on_best: Testing data mode.
        save_on_lowest: Test on data only (no training).
        save_on_highest: Quit when nans or infs found.
        eval_during_train: Saves when highest of this result is found.
        train_mode: Saves when highest of this result is found.
        test_mode: Saves when lowest of this result is found.
        eval_only: Gives results over a training epoch.
        pbar_off: Turn off the progressbar.
    """
	info = pprint.pformat(exp.ARGS)
	logger.info("Starting main loop.")
	if viz.visualizer:
		viz.visualizer.text(info, env=exp.NAME, win="info")
	total_time = 0.0
	if eval_only:
		test_results, test_std = test_epoch("Testing", eval_mode=True, mode=test_mode)
		convert_to_numpy(test_results)
		convert_to_numpy(test_std)
		display_results(test_results, test_std, "Evaluation", None, None, None)
		exit(0)
	best = None
	if not isinstance(epochs, int):
		epochs = epochs["epochs"]
	epoch = exp.INFO["epoch"]
	first_epoch = epoch
	while epoch < epochs:
		try:
			epoch = exp.INFO["epoch"]
			logger.info("Epoch {} / {}".format(epoch, epochs))
			start_time = time.time()
			train_results_ = train_epoch(model, epoch, eval_during_train, data_mode=train_mode, use_pbar=not (pbar_off))
			convert_to_numpy(train_results_)
			update_dict_of_lists(exp.SUMMARY["train"], **train_results_)
			if save_on_best or save_on_highest or save_on_lowest:
				best = save_best(model, train_results_, best, save_on_best, save_on_lowest)
			test_results_ = test_epoch(model, epoch, data_mode=test_mode, use_pbar=not (pbar_off))
			convert_to_numpy(test_results_)
			update_dict_of_lists(exp.SUMMARY["test"], **test_results_)
			align_summaries(exp.SUMMARY["train"], exp.SUMMARY["test"])
			epoch_time = time.time() - start_time
			total_time += epoch_time
			display_results(train_results_, test_results_, epoch, epochs, epoch_time, total_time)
			if viz.visualizer:
				plot(epoch, init=(epoch == first_epoch))
				model.viz.show()
				model.viz.clear()
			if archive_every and epoch % archive_every == 0:
				exp.save(model, prefix=epoch)
			else:
				exp.save(model, prefix="last")
			exp.INFO["epoch"] += 1
		except KeyboardInterrupt:
			def stop_training_query():
				while True:
					try:
						response = input("Keyboard interrupt. Kill? (Y/N) " "(or ^c again)")
					except KeyboardInterrupt:
						return True
					response = response.lower()
					if response == "y":
						return True
					elif response == "n":
						print("Cancelling interrupt. Starting epoch over.")
						return False
					else:
						print("Unknown response")
			kill = stop_training_query()
			if kill:
				print("Training interrupted")
				exp.save(model, prefix="interrupted")
				sys.exit(0)
	logger.info("Successfully completed training")
	exp.save(model, prefix="final")