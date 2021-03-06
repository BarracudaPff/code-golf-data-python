import numpy as np
import GPy
from emukit.quadrature.methods.vanilla_bq import VanillaBayesianQuadrature
from emukit.quadrature.loop.quadrature_loop import VanillaBayesianQuadratureLoop
from emukit.core.loop.user_function import UserFunctionWrapper
from emukit.model_wrappers.gpy_quadrature_wrappers import QuadratureRBF, RBFGPy, BaseGaussianProcessGPy
from numpy.testing import assert_array_equal
def func(x):
	return np.ones((x.shape[0], 1))
def test_vanilla_bq_loop():
	init_size = 5
	x_init = np.random.rand(init_size, 2)
	y_init = np.random.rand(init_size, 1)
	bounds = [(-1, 1), (0, 1)]
	gpy_model = GPy.models.GPRegression(X=x_init, Y=y_init, kernel=GPy.kern.RBF(input_dim=x_init.shape[1], lengthscale=1.0, variance=1.0))
	emukit_qrbf = QuadratureRBF(RBFGPy(gpy_model.kern), integral_bounds=bounds)
	emukit_model = BaseGaussianProcessGPy(kern=emukit_qrbf, gpy_model=gpy_model)
	emukit_method = VanillaBayesianQuadrature(base_gp=emukit_model)
	emukit_loop = VanillaBayesianQuadratureLoop(model=emukit_method)
	num_iter = 5
	emukit_loop.run_loop(user_function=UserFunctionWrapper(func), stopping_condition=num_iter)
	assert emukit_loop.loop_state.X.shape[0] == num_iter + init_size
	assert emukit_loop.loop_state.Y.shape[0] == num_iter + init_size
def test_vanilla_bq_loop_initial_state():
	x_init = np.random.rand(5, 2)
	y_init = np.random.rand(5, 1)
	bounds = [(-1, 1), (0, 1)]
	gpy_model = GPy.models.GPRegression(X=x_init, Y=y_init, kernel=GPy.kern.RBF(input_dim=x_init.shape[1], lengthscale=1.0, variance=1.0))
	emukit_qrbf = QuadratureRBF(RBFGPy(gpy_model.kern), integral_bounds=bounds)
	emukit_model = BaseGaussianProcessGPy(kern=emukit_qrbf, gpy_model=gpy_model)
	emukit_method = VanillaBayesianQuadrature(base_gp=emukit_model)
	emukit_loop = VanillaBayesianQuadratureLoop(model=emukit_method)
	assert_array_equal(emukit_loop.loop_state.X, x_init)
	assert_array_equal(emukit_loop.loop_state.Y, y_init)
	assert emukit_loop.loop_state.iteration == 0