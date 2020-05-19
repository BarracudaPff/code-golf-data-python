def test_circular_gaussian_return_shape():
	"""
    Test output dimension is 2d
    """
	circular_gaussian_func, _ = circular_gaussian()
	x = np.ones((3, 2))
	result = circular_gaussian_func.f(x)
	assert result.ndim == 2
	assert result.shape == (3, 1)