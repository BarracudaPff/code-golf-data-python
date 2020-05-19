"""Convert lowered IR basic blocks to MATCH query strings."""
from collections import deque
import six
from .blocks import Filter, MarkLocation, QueryRoot, Recurse, Traverse
from .expressions import TrueLiteral
from .helpers import get_only_element_from_collection, validate_safe_string
def _get_vertex_location_name(location):
	"""Get the location name from a location that is expected to point to a vertex."""
	mark_name, field_name = location.get_location_name()
	if field_name is not None:
		raise AssertionError(u"Location unexpectedly pointed to a field: {}".format(location))
	return mark_name
def _first_step_to_match(match_step):
	"""Transform the very first MATCH step into a MATCH query string."""
	parts = []
	if match_step.root_block is not None:
		if not isinstance(match_step.root_block, QueryRoot):
			raise AssertionError(u"Expected None or QueryRoot root block, received: " u"{} {}".format(match_step.root_block, match_step))
		match_step.root_block.validate()
		start_class = get_only_element_from_collection(match_step.root_block.start_class)
		parts.append(u"class: %s" % (start_class,))
	if match_step.coerce_type_block is not None:
		raise AssertionError(u"Invalid MATCH step: {}".format(match_step))
	if match_step.where_block:
		match_step.where_block.validate()
		parts.append(u"where: (%s)" % (match_step.where_block.predicate.to_match(),))
	if match_step.as_block is None:
		raise AssertionError(u"Found a MATCH step without a corresponding Location. " u"This should never happen: {}".format(match_step))
	else:
		match_step.as_block.validate()
		parts.append(u"as: %s" % (_get_vertex_location_name(match_step.as_block.location),))
	return u"{{ %s }}" % (u", ".join(parts),)
def _subsequent_step_to_match(match_step):
	"""Transform any subsequent (non-first) MATCH step into a MATCH query string."""
	if not isinstance(match_step.root_block, (Traverse, Recurse)):
		raise AssertionError(u"Expected Traverse root block, received: " u"{} {}".format(match_step.root_block, match_step))
	is_recursing = isinstance(match_step.root_block, Recurse)
	match_step.root_block.validate()
	traversal_command = u".%s('%s')" % (match_step.root_block.direction, match_step.root_block.edge_name)
	parts = []
	if match_step.coerce_type_block:
		coerce_type_set = match_step.coerce_type_block.target_class
		if len(coerce_type_set) != 1:
			raise AssertionError(u"Found MATCH type coercion block with more than one target class:" u" {} {}".format(coerce_type_set, match_step))
		coerce_type_target = list(coerce_type_set)[0]
		parts.append(u"class: %s" % (coerce_type_target,))
	if is_recursing:
		parts.append(u"while: ($depth < %d)" % (match_step.root_block.depth,))
	if match_step.where_block:
		match_step.where_block.validate()
		parts.append(u"where: (%s)" % (match_step.where_block.predicate.to_match(),))
	if not is_recursing and match_step.root_block.optional:
		parts.append(u"optional: true")
	if match_step.as_block:
		match_step.as_block.validate()
		parts.append(u"as: %s" % (_get_vertex_location_name(match_step.as_block.location),))
	return u"%s {{ %s }}" % (traversal_command, u", ".join(parts))
def _represent_match_traversal(match_traversal):
	"""Emit MATCH query code for an entire MATCH traversal sequence."""
	output = []
	output.append(_first_step_to_match(match_traversal[0]))
	for step in match_traversal[1:]:
		output.append(_subsequent_step_to_match(step))
	return u"".join(output)
def _represent_fold(fold_location, fold_ir_blocks):
	"""Emit a LET clause corresponding to the IR blocks for a @fold scope."""
	start_let_template = u"$%(mark_name)s = %(base_location)s"
	traverse_edge_template = u'.%(direction)s("%(edge_name)s")'
	base_template = start_let_template + traverse_edge_template
	edge_direction, edge_name = fold_location.get_first_folded_edge()
	mark_name, _ = fold_location.get_location_name()
	base_location_name, _ = fold_location.base_location.get_location_name()
	validate_safe_string(mark_name)
	validate_safe_string(base_location_name)
	validate_safe_string(edge_direction)
	validate_safe_string(edge_name)
	template_data = {"mark_name": mark_name, "base_location": base_location_name, "direction": edge_direction, "edge_name": edge_name}
	final_string = base_template % template_data
	for block in fold_ir_blocks:
		if isinstance(block, Filter):
			final_string += u"[" + block.predicate.to_match() + u"]"
		elif isinstance(block, Traverse):
			template_data = {"direction": block.direction, "edge_name": block.edge_name}
			final_string += traverse_edge_template % template_data
		elif isinstance(block, MarkLocation):
			pass
		else:
			raise AssertionError(u"Found an unexpected IR block in the folded IR blocks: " u"{} {} {}".format(type(block), block, fold_ir_blocks))
	final_string += ".asList()"
	return final_string
def _construct_output_to_match(output_block):
	"""Transform a ConstructResult block into a MATCH query string."""
	output_block.validate()
	selections = (u"%s AS `%s`" % (output_block.fields[key].to_match(), key) for key in sorted(output_block.fields.keys()))
	return u"SELECT %s FROM" % (u", ".join(selections),)
def _construct_where_to_match(where_block):
	"""Transform a Filter block into a MATCH query string."""
	if where_block.predicate == TrueLiteral:
		raise AssertionError(u"Received WHERE block with TrueLiteral predicate: {}".format(where_block))
	return u"WHERE " + where_block.predicate.to_match()
def emit_code_from_single_match_query(match_query):
	"""Return a MATCH query string from a list of IR blocks."""
	query_data = deque([u"MATCH "])
	if not match_query.match_traversals:
		raise AssertionError(u"Unexpected falsy value for match_query.match_traversals received: " u"{} {}".format(match_query.match_traversals, match_query))
	match_traversal_data = [_represent_match_traversal(x) for x in match_query.match_traversals]
	query_data.append(match_traversal_data[0])
	for traversal_data in match_traversal_data[1:]:
		query_data.append(u", ")
		query_data.append(traversal_data)
	query_data.appendleft(u" (")
	query_data.append(u"RETURN $matches)")
	fold_data = sorted([_represent_fold(fold_location, fold_ir_blocks) for fold_location, fold_ir_blocks in six.iteritems(match_query.folds)])
	if fold_data:
		query_data.append(u" LET ")
		query_data.append(fold_data[0])
		for fold_clause in fold_data[1:]:
			query_data.append(u", ")
			query_data.append(fold_clause)
	query_data.appendleft(_construct_output_to_match(match_query.output_block))
	if match_query.where_block is not None:
		query_data.append(_construct_where_to_match(match_query.where_block))
	return u" ".join(query_data)
def emit_code_from_multiple_match_queries(match_queries):
	"""Return a MATCH query string from a list of MatchQuery namedtuples."""
	optional_variable_base_name = "$optional__"
	union_variable_name = "$result"
	query_data = deque([u"SELECT EXPAND(", union_variable_name, u")", u" LET "])
	optional_variables = []
	sub_queries = [emit_code_from_single_match_query(match_query) for match_query in match_queries]
	for (i, sub_query) in enumerate(sub_queries):
		variable_name = optional_variable_base_name + str(i)
		variable_assignment = variable_name + u" = ("
		sub_query_end = u"),"
		query_data.append(variable_assignment)
		query_data.append(sub_query)
		query_data.append(sub_query_end)
		optional_variables.append(variable_name)
	query_data.append(union_variable_name)
	query_data.append(u" = UNIONALL(")
	query_data.append(u", ".join(optional_variables))
	query_data.append(u")")
	return u" ".join(query_data)
def emit_code_from_ir(schema_info, compound_match_query):
	"""Return a MATCH query string from a CompoundMatchQuery."""
	match_queries = compound_match_query.match_queries
	if len(match_queries) == 1:
		query_string = emit_code_from_single_match_query(match_queries[0])
	elif len(match_queries) > 1:
		query_string = emit_code_from_multiple_match_queries(match_queries)
	else:
		raise AssertionError(u"Received CompoundMatchQuery with an empty list of MatchQueries: " u"{}".format(match_queries))
	return query_string