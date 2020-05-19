"""Safely represent arguments for Gremlin-language GraphQL queries."""
def _safe_gremlin_string(value):
	"""Sanitize and represent a string argument in Gremlin."""
	if not isinstance(value, six.string_types):
		if isinstance(value, bytes):
			value = value.decode("utf-8")
		else:
			raise GraphQLInvalidArgumentError(u"Attempting to convert a non-string into a string: " u"{}".format(value))
	escaped_and_quoted = json.dumps(value)
	if not escaped_and_quoted[0] == escaped_and_quoted[-1] == '"':
		raise AssertionError(u"Unreachable state reached: {} {}".format(value, escaped_and_quoted))
	no_quotes = escaped_and_quoted[1:-1]
	re_escaped = no_quotes.replace('\\"', '"').replace("'", "\\'")
	final_escaped_value = "'" + re_escaped + "'"
	return final_escaped_value
def _safe_gremlin_decimal(value):
	"""Represent decimal objects as Gremlin strings."""
	decimal_value = coerce_to_decimal(value)
	return str(decimal_value) + "G"
def _safe_gremlin_date_and_datetime(graphql_type, expected_python_types, value):
	"""Represent date and datetime objects as Gremlin strings."""
	value_type = type(value)
	if not any(value_type == x for x in expected_python_types):
		raise GraphQLInvalidArgumentError(u"Expected value to be exactly one of " u"python types {}, but was {}: " u"{}".format(expected_python_types, value_type, value))
	try:
		serialized_value = graphql_type.serialize(value)
	except ValueError as e:
		raise GraphQLInvalidArgumentError(e)
	return _safe_gremlin_string(serialized_value)
def _safe_gremlin_list(inner_type, argument_value):
	"""Represent the list of "inner_type" objects in Gremlin form."""
	if not isinstance(argument_value, list):
		raise GraphQLInvalidArgumentError(u"Attempting to represent a non-list as a list: " u"{}".format(argument_value))
	stripped_type = strip_non_null_from_type(inner_type)
	components = (_safe_gremlin_argument(stripped_type, x) for x in argument_value)
	return u"[" + u",".join(components) + u"]"
def _safe_gremlin_argument(expected_type, argument_value):
	"""Return a Gremlin string representing the given argument value."""
	if GraphQLString.is_same_type(expected_type):
		return _safe_gremlin_string(argument_value)
	elif GraphQLID.is_same_type(expected_type):
		if not isinstance(argument_value, six.string_types):
			if isinstance(argument_value, bytes):
				argument_value = argument_value.decode("utf-8")
			else:
				argument_value = six.text_type(argument_value)
		return _safe_gremlin_string(argument_value)
	elif GraphQLFloat.is_same_type(expected_type):
		return represent_float_as_str(argument_value)
	elif GraphQLInt.is_same_type(expected_type):
		if isinstance(argument_value, bool):
			raise GraphQLInvalidArgumentError(u"Attempting to represent a non-int as an int: " u"{}".format(argument_value))
		return type_check_and_str(int, argument_value)
	elif GraphQLBoolean.is_same_type(expected_type):
		return type_check_and_str(bool, argument_value)
	elif GraphQLDecimal.is_same_type(expected_type):
		return _safe_gremlin_decimal(argument_value)
	elif GraphQLDate.is_same_type(expected_type):
		return _safe_gremlin_date_and_datetime(expected_type, (datetime.date,), argument_value)
	elif GraphQLDateTime.is_same_type(expected_type):
		return _safe_gremlin_date_and_datetime(expected_type, (datetime.datetime, arrow.Arrow), argument_value)
	elif isinstance(expected_type, GraphQLList):
		return _safe_gremlin_list(expected_type.of_type, argument_value)
	else:
		raise AssertionError(u"Could not safely represent the requested GraphQL type: " u"{} {}".format(expected_type, argument_value))
def insert_arguments_into_gremlin_query(compilation_result, arguments):
	"""Insert the arguments into the compiled Gremlin query to form a complete query.
    The GraphQL compiler attempts to use single-quoted string literals ('abc') in Gremlin output.
    Double-quoted strings allow inline interpolation with the $ symbol, see here for details:
    http://www.groovy-lang.org/syntax.html#all-strings
    If the compiler needs to emit a literal '$' character as part of the Gremlin query,
    it must be doubled ('$$') to avoid being interpreted as a query parameter.
    Args:
        compilation_result: a CompilationResult object derived from the GraphQL compiler
        arguments: dict, str -> any, mapping argument name to its value, for every parameter the
                   query expects.
    Returns:
        string, a Gremlin query with inserted argument data
    """
	if compilation_result.language != GREMLIN_LANGUAGE:
		raise AssertionError(u"Unexpected query output language: {}".format(compilation_result))
	base_query = compilation_result.query
	argument_types = compilation_result.input_metadata
	sanitized_arguments = {key: _safe_gremlin_argument(argument_types[key], value) for key, value in six.iteritems(arguments)}
	return Template(base_query).substitute(sanitized_arguments)