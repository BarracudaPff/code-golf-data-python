def pretty_print_graphql(query, use_four_spaces=True):
	"""Take a GraphQL query, pretty print it, and return it."""
	output = visit(parse(query), CustomPrintingVisitor())
	if use_four_spaces:
		return fix_indentation_depth(output)
	return output
DIRECTIVES_BY_NAME = {d.name: d for d in DIRECTIVES}
class CustomPrintingVisitor(PrintingVisitor):
	def leave_Directive(self, node, *args):
		"""Call when exiting a directive node in the ast."""
		name_to_arg_value = {arg.split(":", 1)[0]: arg for arg in node.arguments}
		ordered_args = node.arguments
		directive = DIRECTIVES_BY_NAME.get(node.name)
		if directive:
			sorted_args = []
			encountered_argument_names = set()
			for defined_arg_name in six.iterkeys(directive.args):
				if defined_arg_name in name_to_arg_value:
					encountered_argument_names.add(defined_arg_name)
					sorted_args.append(name_to_arg_value[defined_arg_name])
			unsorted_args = [value for name, value in six.iteritems(name_to_arg_value) if name not in encountered_argument_names]
			ordered_args = sorted_args + unsorted_args
		return "@" + node.name + wrap("(", join(ordered_args, ", "), ")")
def fix_indentation_depth(query):
	"""Make indentation use 4 spaces, rather than the 2 spaces GraphQL normally uses."""
	lines = query.split("\n")
	final_lines = []
	for line in lines:
		consecutive_spaces = 0
		for char in line:
			if char == " ":
				consecutive_spaces += 1
			else:
				break
		if consecutive_spaces % 2 != 0:
			raise AssertionError(u"Indentation was not a multiple of two: " u"{}".format(consecutive_spaces))
		final_lines.append(("  " * consecutive_spaces) + line[consecutive_spaces:])
	return "\n".join(final_lines)