__all__ = ["test_normal_walk", "test_uniform_walk"]
def test_normal_walk(**kwargs):
	_test_normal(moves.WalkMove(s=3), **kwargs)
def test_uniform_walk(**kwargs):
	_test_uniform(moves.WalkMove(s=3), **kwargs)