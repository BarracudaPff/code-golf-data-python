import numpy as np
def gradient_check_numpy_expr(func, x, output_gradient, h=1e-5):
	"""
    This utility function calculates gradient of the function `func`
    at `x`.
    :param func:
    :param x:
    :param output_gradient:
    :param h:
    :return:
    """
	grad = np.zeros_like(x).astype(np.float32)
	iter = np.nditer(x, flags=["multi_index"], op_flags=["readwrite"])
	while not iter.finished:
		idx = iter.multi_index
		old_value = x[idx]
		x[idx] = old_value + h
		pos = func(x).copy()
		x[idx] = old_value - h
		neg = func(x).copy()
		x[idx] = old_value
		grad[idx] = np.sum((np.array(pos) - np.array(neg)) * output_gradient) / (2 * h)
		iter.iternext()
	return grad