def test_random_search_acquisition_optimizer(simple_square_acquisition):
	space = ParameterSpace([CategoricalParameter("x", OrdinalEncoding(np.arange(0, 100)))])
	optimizer = RandomSearchAcquisitionOptimizer(space, 1000)
	opt_x, opt_val = optimizer.optimize(simple_square_acquisition)
	assert_array_equal(opt_x, np.array([[1.0]]))
	assert_array_equal(opt_val, np.array([[0.0]]))
def test_random_search_acquisition_optimizer_with_context(simple_square_acquisition):
	space = ParameterSpace([CategoricalParameter("x", OrdinalEncoding(np.arange(0, 100))), InformationSourceParameter(10)])
	optimizer = RandomSearchAcquisitionOptimizer(space, 1000)
	source_encoding = 1
	opt_x, opt_val = optimizer.optimize(simple_square_acquisition, {"source": source_encoding})
	assert_array_equal(opt_x, np.array([[1.0, source_encoding]]))
	assert_array_equal(opt_val, np.array([[0.0 + source_encoding]]))