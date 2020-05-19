"""
 linear_regression_SGD.py  (author: Anson Wong / git: ankonzoid)
"""
import os
import numpy as np
import pandas as pd
class LinearRegressorSGD:
	def __init__(self):
		pass
	def fit(self, X, y):
		print("Fitting...")
		N, d = X.shape
		a_fit = np.random.normal(size=d + 1)
		loss_tolerance = 1e-6
		fit_tolerance = 1e-4
		eta = 1e-6
		converge = False
		loss = 9e99
		iter = 0
		while not converge:
			i_random = np.random.choice(N)
			gradient = np.zeros(d + 1)
			y_hat_i = a_fit[0] + np.dot(a_fit[1:], X[i_random])
			y_i = y[i_random]
			gradient[0] += 2 * (y_hat_i - y_i)
			gradient[1:] += 2 * (y_hat_i - y_i) * X[i_random, 0:]
			a_fit_new = a_fit - eta * gradient
			y_pred = []
			for x in X:
				y_pred_i = a_fit_new[0] + np.dot(a_fit_new[1:], x)
				y_pred.append(y_pred_i)
			y_pred = np.array(y_pred)
			loss_new = np.linalg.norm(y_pred - y) ** 2 / N
			if iter % N:
				print("loss = {}".format(loss))
			if np.abs(loss_new - loss) < loss_tolerance and np.linalg.norm(a_fit_new - a_fit) < fit_tolerance:
				converge = True
			a_fit = a_fit_new
			loss = loss_new
			iter += 1
		self.a_fit = a_fit
	def predict(self, X):
		y_pred = []
		for x in X:
			y_pred_i = self.a_fit[0] + np.dot(self.a_fit[1:], x)
			y_pred.append(y_pred_i)
		y_pred = np.array(y_pred)
		return y_pred
if __name__ == "__main__":
	X = np.arange(100).reshape(-1, 1)
	y = 0.4 * X.flatten() + 3 + np.random.uniform(-10, 10, size=(100,))
	model = LinearRegressorSGD()
	model.fit(X, y)
	y_pred = model.predict(X)
	mse = ((y_pred - y) ** 2).mean(axis=0)
	print("mse =", mse)
	import matplotlib.pyplot as plt
	plt.figure(1)
	plt.plot(X.flatten(), y, "o")
	plt.plot(X.flatten(), y_pred, "r")
	plt.show()