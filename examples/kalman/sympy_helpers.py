def cross(x):
	ret = sp.Matrix(np.zeros((3, 3)))
	ret[0, 1], ret[0, 2] = -x[2], x[1]
	ret[1, 0], ret[1, 2] = x[2], -x[0]
	ret[2, 0], ret[2, 1] = -x[1], x[0]
	return ret
def euler_rotate(roll, pitch, yaw):
	matrix_roll = sp.Matrix([[1, 0, 0], [0, sp.cos(roll), -sp.sin(roll)], [0, sp.sin(roll), sp.cos(roll)]])
	matrix_pitch = sp.Matrix([[sp.cos(pitch), 0, sp.sin(pitch)], [0, 1, 0], [-sp.sin(pitch), 0, sp.cos(pitch)]])
	matrix_yaw = sp.Matrix([[sp.cos(yaw), -sp.sin(yaw), 0], [sp.sin(yaw), sp.cos(yaw), 0], [0, 0, 1]])
	return matrix_yaw * matrix_pitch * matrix_roll
def quat_rotate(q0, q1, q2, q3):
	return sp.Matrix([[q0 ** 2 + q1 ** 2 - q2 ** 2 - q3 ** 2, 2 * (q1 * q2 + q0 * q3), 2 * (q1 * q3 - q0 * q2)], [2 * (q1 * q2 - q0 * q3), q0 ** 2 - q1 ** 2 + q2 ** 2 - q3 ** 2, 2 * (q2 * q3 + q0 * q1)], [2 * (q1 * q3 + q0 * q2), 2 * (q2 * q3 - q0 * q1), q0 ** 2 - q1 ** 2 - q2 ** 2 + q3 ** 2]]).T
def quat_matrix_l(p):
	return sp.Matrix([[p[0], -p[1], -p[2], -p[3]], [p[1], p[0], -p[3], p[2]], [p[2], p[3], p[0], -p[1]], [p[3], -p[2], p[1], p[0]]])
def quat_matrix_r(p):
	return sp.Matrix([[p[0], -p[1], -p[2], -p[3]], [p[1], p[0], p[3], -p[2]], [p[2], -p[3], p[0], p[1]], [p[3], p[2], -p[1], p[0]]])
def sympy_into_c(sympy_functions):
	routines = []
	for name, expr, args in sympy_functions:
		r = codegen.make_routine(name, expr, language="C99")
		nargs = []
		for aa in args:
			if aa is None:
				nargs.append(codegen.InputArgument(sp.Symbol("unused"), dimensions=[1, 1]))
				continue
			found = False
			for a in r.arguments:
				if str(aa.name) == str(a.name):
					nargs.append(a)
					found = True
					break
			if not found:
				nargs.append(codegen.InputArgument(aa, dimensions=[1, 1]))
		for a in r.arguments:
			if type(a) == codegen.OutputArgument:
				nargs.append(a)
		r.arguments = nargs
		routines.append(r)
	[(c_name, c_code), (h_name, c_header)] = codegen.get_code_generator("C", "ekf", "C99").write(routines, "ekf")
	c_code = "\n".join(filter(lambda x: len(x) > 0 and x[0] != "#", c_code.split("\n")))
	c_header = "\n".join(filter(lambda x: len(x) > 0 and x[0] != "#", c_header.split("\n")))
	return c_header, c_code