"""
Creates the swig_doc.i SWIG interface file.
Execute using: python swig_doc.py xml_path outputfilename
The file instructs SWIG to transfer the doxygen comments into the
python docstrings.
"""
import sys
try:
	from doxyxml import DoxyIndex, DoxyClass, DoxyFriend, DoxyFunction, DoxyFile, base
except ImportError:
	from gnuradio.doxyxml import DoxyIndex, DoxyClass, DoxyFriend, DoxyFunction, DoxyFile, base
def py_name(name):
	bits = name.split("_")
	return "_".join(bits[1:])
def make_name(name):
	bits = name.split("_")
	return bits[0] + "_make_" + "_".join(bits[1:])
class Block(object):
	"""
    Checks if doxyxml produced objects correspond to a gnuradio block.
    """
	@classmethod
	def includes(cls, item):
		if not isinstance(item, DoxyClass):
			return False
		if item.error():
			return False
		return item.has_member(make_name(item.name()), DoxyFriend)
def utoascii(text):
	"""
    Convert unicode text into ascii and escape quotes.
    """
	if text is None:
		return ""
	out = text.encode("ascii", "replace")
	out = out.replace('"', '\\"')
	return out
def combine_descriptions(obj):
	"""
    Combines the brief and detailed descriptions of an object together.
    """
	description = []
	bd = obj.brief_description.strip()
	dd = obj.detailed_description.strip()
	if bd:
		description.append(bd)
	if dd:
		description.append(dd)
	return utoascii("\n\n".join(description)).strip()
entry_templ = '%feature("docstring") {name} "{docstring}"'
def make_entry(obj, name=None, templ="{description}", description=None):
	"""
    Create a docstring entry for a swig interface file.
    obj - a doxyxml object from which documentation will be extracted.
    name - the name of the C object (defaults to obj.name())
    templ - an optional template for the docstring containing only one
            variable named 'description'.
    description - if this optional variable is set then it's value is
            used as the description instead of extracting it from obj.
    """
	if name is None:
		name = obj.name()
	if "operator " in name:
		return ""
	if description is None:
		description = combine_descriptions(obj)
	docstring = templ.format(description=description)
	if not docstring:
		return ""
	return entry_templ.format(name=name, docstring=docstring)
def make_func_entry(func, name=None, description=None, params=None):
	"""
    Create a function docstring entry for a swig interface file.
    func - a doxyxml object from which documentation will be extracted.
    name - the name of the C object (defaults to func.name())
    description - if this optional variable is set then it's value is
            used as the description instead of extracting it from func.
    params - a parameter list that overrides using func.params.
    """
	if params is None:
		params = func.params
	params = [prm.declname for prm in params]
	if params:
		sig = "Params: (%s)" % ", ".join(params)
	else:
		sig = "Params: (NONE)"
	templ = "{description}\n\n" + sig
	return make_entry(func, name=name, templ=utoascii(templ), description=description)
def make_class_entry(klass, description=None):
	"""
    Create a class docstring for a swig interface file.
    """
	output = []
	output.append(make_entry(klass, description=description))
	for func in klass.in_category(DoxyFunction):
		name = klass.name() + "::" + func.name()
		output.append(make_func_entry(func, name=name))
	return "\n\n".join(output)
def make_block_entry(di, block):
	"""
    Create class and function docstrings of a gnuradio block for a
    swig interface file.
    """
	descriptions = []
	class_desc = combine_descriptions(block)
	if class_desc:
		descriptions.append(class_desc)
	make_func = di.get_member(make_name(block.name()), DoxyFunction)
	make_func_desc = combine_descriptions(make_func)
	if make_func_desc:
		descriptions.append(make_func_desc)
	try:
		block_file = di.get_member(block.name() + ".h", DoxyFile)
		file_desc = combine_descriptions(block_file)
		if file_desc:
			descriptions.append(file_desc)
	except base.Base.NoSuchMember:
		pass
	super_description = "\n\n".join(descriptions)
	output = []
	output.append(make_class_entry(block, description=super_description))
	creator = block.get_member(block.name(), DoxyFunction)
	output.append(make_func_entry(make_func, description=super_description, params=creator.params))
	return "\n\n".join(output)
def make_swig_interface_file(di, swigdocfilename, custom_output=None):
	output = [
		"""
/*
 * This file was automatically generated using swig_doc.py.
 *
 * Any changes to it will be lost next time it is regenerated.
 */
"""
	]
	if custom_output is not None:
		output.append(custom_output)
	blocks = di.in_category(Block)
	make_funcs = set([])
	for block in blocks:
		try:
			make_func = di.get_member(make_name(block.name()), DoxyFunction)
			make_funcs.add(make_func.name())
			output.append(make_block_entry(di, block))
		except block.ParsingError:
			print("Parsing error for block %s" % block.name())
	funcs = [f for f in di.in_category(DoxyFunction) if f.name() not in make_funcs]
	for f in funcs:
		try:
			output.append(make_func_entry(f))
		except f.ParsingError:
			print("Parsing error for function %s" % f.name())
	block_names = [block.name() for block in blocks]
	klasses = [k for k in di.in_category(DoxyClass) if k.name() not in block_names]
	for k in klasses:
		try:
			output.append(make_class_entry(k))
		except k.ParsingError:
			print("Parsing error for class %s" % k.name())
	output = "\n\n".join(output)
	swig_doc = file(swigdocfilename, "w")
	swig_doc.write(output)
	swig_doc.close()
if __name__ == "__main__":
	err_msg = "Execute using: python swig_doc.py xml_path outputfilename"
	if len(sys.argv) != 3:
		raise StandardError(err_msg)
	xml_path = sys.argv[1]
	swigdocfilename = sys.argv[2]
	di = DoxyIndex(xml_path)
	output = []
	custom_output = "\n\n".join(output)
	make_swig_interface_file(di, swigdocfilename, custom_output=custom_output)