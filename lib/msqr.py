def modular_sqrt(a, p):
	""" Find a quadratic residue (mod p) of 'a'. p
    must be an odd prime.
    Solve the congruence of the form:
    x^2 = a (mod p)
    And returns x. Note that p - x is also a root.
    0 is returned is no square root exists for
    these a and p.
    The Tonelli-Shanks algorithm is used (except
    for some simple cases in which the solution
    is known from an identity). This algorithm
    runs in polynomial time (unless the
    generalized Riemann hypothesis is false).
    """
	if legendre_symbol(a, p) != 1:
		return 0
	elif a == 0:
		return 0
	elif p == 2:
		return p
	elif p % 4 == 3:
		return pow(a, (p + 1) // 4, p)
	s = p - 1
	e = 0
	while s % 2 == 0:
		s //= 2
		e += 1
	n = 2
	while legendre_symbol(n, p) != -1:
		n += 1
	x = pow(a, (s + 1) // 2, p)
	b = pow(a, s, p)
	g = pow(n, s, p)
	r = e
	while True:
		t = b
		m = 0
		for m in range(r):
			if t == 1:
				break
			t = pow(t, 2, p)
		if m == 0:
			return x
		gs = pow(g, 2 ** (r - m - 1), p)
		g = (gs * gs) % p
		x = (x * gs) % p
		b = (b * g) % p
		r = m
def legendre_symbol(a, p):
	""" Compute the Legendre symbol a|p using
    Euler's criterion. p is a prime, a is
    relatively prime to p (if p divides
    a, then a|p = 0)
    Returns 1 if a has a square root modulo
    p, -1 otherwise.
    """
	ls = pow(a, (p - 1) // 2, p)
	return -1 if ls == p - 1 else ls