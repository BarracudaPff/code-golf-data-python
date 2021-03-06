"""Diff rendering in HTML for Rietveld."""
import cgi
import difflib
import re
from google.appengine.ext import db
from google.appengine.ext import ndb
from django.conf import settings
from django.template import loader, RequestContext
from codereview import auth_utils
from codereview import intra_region_diff
from codereview import models
from codereview import patching
from codereview import utils
def SplitPatch(data):
	"""Splits a patch into separate pieces for each file.
  Args:
    data: A string containing the output of svn diff.
  Returns:
    A list of 2-tuple (filename, text) where text is the svn diff output
      pertaining to filename.
  """
	patches = []
	filename = None
	diff = []
	for line in data.splitlines(True):
		new_filename = None
		if line.startswith("Index:"):
			_, new_filename = line.split(":", 1)
			new_filename = new_filename.strip()
		elif line.startswith("Property changes on:"):
			_, temp_filename = line.split(":", 1)
			temp_filename = temp_filename.strip().replace("\\", "/")
			if temp_filename != filename:
				new_filename = temp_filename
		if new_filename:
			if filename and diff:
				patches.append((filename, "".join(diff)))
			filename = new_filename
			diff = [line]
			continue
		if diff is not None:
			diff.append(line)
	if filename and diff:
		patches.append((filename, "".join(diff)))
	return patches
def ParsePatchSet(patchset):
	"""Patch a patch set into individual patches.
  Args:
    patchset: a models.PatchSet instance.
  Returns:
    A list of models.Patch instances.
  """
	patches = []
	ps_key = patchset.key
	splitted = SplitPatch(patchset.data)
	if not splitted:
		return []
	first_id, last_id = models.Patch.allocate_ids(len(splitted), parent=ps_key)
	ids = range(first_id, last_id + 1)
	for filename, text in splitted:
		key = ndb.Key(models.Patch, ids.pop(0), parent=ps_key)
		patches.append(models.Patch(patchset_key=patchset.key, text=utils.to_dbtext(text), filename=filename, key=key))
	return patches
def RenderDiffTableRows(request, old_lines, chunks, patch, colwidth=settings.DEFAULT_COLUMN_WIDTH, debug=False, context=settings.DEFAULT_CONTEXT):
	"""Render the HTML table rows for a side-by-side diff for a patch.
  Args:
    request: Django Request object.
    old_lines: List of lines representing the original file.
    chunks: List of chunks as returned by patching.ParsePatchToChunks().
    patch: A models.Patch instance.
    colwidth: Optional column width (default 80).
    debug: Optional debugging flag (default False).
    context: Maximum number of rows surrounding a change (default CONTEXT).
  Yields:
    Strings, each of which represents the text rendering one complete
    pair of lines of the side-by-side diff, possibly including comments.
    Each yielded string may consist of several <tr> elements.
  """
	rows = _RenderDiffTableRows(request, old_lines, chunks, patch, colwidth, debug)
	return _CleanupTableRowsGenerator(rows, context)
def RenderDiff2TableRows(request, old_lines, old_patch, new_lines, new_patch, colwidth=settings.DEFAULT_COLUMN_WIDTH, debug=False, context=settings.DEFAULT_CONTEXT):
	"""Render the HTML table rows for a side-by-side diff between two patches.
  Args:
    request: Django Request object.
    old_lines: List of lines representing the patched file on the left.
    old_patch: The models.Patch instance corresponding to old_lines.
    new_lines: List of lines representing the patched file on the right.
    new_patch: The models.Patch instance corresponding to new_lines.
    colwidth: Optional column width (default 80).
    debug: Optional debugging flag (default False).
    context: Maximum number of visible context lines (default
      settings.DEFAULT_CONTEXT).
  Yields:
    Strings, each of which represents the text rendering one complete
    pair of lines of the side-by-side diff, possibly including comments.
    Each yielded string may consist of several <tr> elements.
  """
	rows = _RenderDiff2TableRows(request, old_lines, old_patch, new_lines, new_patch, colwidth, debug)
	return _CleanupTableRowsGenerator(rows, context)
def _CleanupTableRowsGenerator(rows, context):
	"""Cleanup rows returned by _TableRowGenerator for output.
  Args:
    rows: List of tuples (tag, text)
    context: Maximum number of visible context lines.
  Yields:
    Rows marked as 'equal' are possibly contracted using _ShortenBuffer().
    Stops on rows marked as 'error'.
  """
	buf = []
	for tag, text in rows:
		if tag == "equal":
			buf.append(text)
			continue
		else:
			for t in _ShortenBuffer(buf, context):
				yield t
			buf = []
		yield text
		if tag == "error":
			yield None
			break
	if buf:
		for t in _ShortenBuffer(buf, context):
			yield t
def _ShortenBuffer(buf, context):
	"""Render a possibly contracted series of HTML table rows.
  Args:
    buf: a list of strings representing HTML table rows.
    context: Maximum number of visible context lines. If None all lines are
      returned.
  Yields:
    If the buffer has fewer than 3 times context items, yield all
    the items.  Otherwise, yield the first context items, a single
    table row representing the contraction, and the last context
    items.
  """
	if context is None or len(buf) < 3 * context:
		for t in buf:
			yield t
	else:
		last_id = None
		for t in buf[:context]:
			m = re.match('^<tr( name="hook")? id="pair-(?P<rowcount>\d+)">', t)
			if m:
				last_id = int(m.groupdict().get("rowcount"))
			yield t
		skip = len(buf) - 2 * context
		expand_link = []
		if skip > 3 * context:
			expand_link.append(('<a href="javascript:M_expandSkipped(%(before)d, ' "%(after)d, 't', %(skip)d)\">" "Expand %(context)d before" "</a> | "))
		expand_link.append(('<a href="javascript:M_expandSkipped(%(before)d, ' "%(after)d, 'a', %(skip)d)\">Expand all</a>"))
		if skip > 3 * context:
			expand_link.append((" | " '<a href="javascript:M_expandSkipped(%(before)d, ' "%(after)d, 'b', %(skip)d)\">" "Expand %(context)d after" "</a>"))
		expand_link = "".join(expand_link) % {"before": last_id + 1, "after": last_id + skip, "skip": last_id, "context": max(context, None)}
		yield ('<tr id="skip-%d"><td colspan="2" align="center" ' 'style="background:lightblue">' '(...skipping <span id="skipcount-%d">%d</span> matching lines...) ' '<span id="skiplinks-%d">%s</span>  ' '<span id="skiploading-%d" style="visibility:hidden;">Loading...' "</span>" "</td></tr>\n" % (last_id, last_id, skip, last_id, expand_link, last_id))
		for t in buf[-context:]:
			yield t
def _RenderDiff2TableRows(request, old_lines, old_patch, new_lines, new_patch, colwidth=settings.DEFAULT_COLUMN_WIDTH, debug=False):
	"""Internal version of RenderDiff2TableRows().
  Args:
    The same as for RenderDiff2TableRows.
  Yields:
    Tuples (tag, row) where tag is an indication of the row type.
  """
	old_dict = {}
	new_dict = {}
	for patch, dct in [(old_patch, old_dict), (new_patch, new_dict)]:
		if patch:
			query = models.Comment.query(models.Comment.patch_key == patch.key, models.Comment.left == False).order(models.Comment.date)
			for comment in query:
				if comment.draft and comment.author != request.user:
					continue
				comment.complete()
				lst = dct.setdefault(comment.lineno, [])
				lst.append(comment)
	return _TableRowGenerator(old_patch, old_dict, len(old_lines) + 1, "new", new_patch, new_dict, len(new_lines) + 1, "new", _GenerateTriples(old_lines, new_lines), colwidth, debug, request)
def _GenerateTriples(old_lines, new_lines):
	"""Helper for _RenderDiff2TableRows yielding input for _TableRowGenerator.
  Args:
    old_lines: List of lines representing the patched file on the left.
    new_lines: List of lines representing the patched file on the right.
  Yields:
    Tuples (tag, old_slice, new_slice) where tag is a tag as returned by
    difflib.SequenceMatchser.get_opcodes(), and old_slice and new_slice
    are lists of lines taken from old_lines and new_lines.
  """
	sm = difflib.SequenceMatcher(None, old_lines, new_lines)
	for tag, i1, i2, j1, j2 in sm.get_opcodes():
		yield tag, old_lines[i1:i2], new_lines[j1:j2]
def _GetComments(request):
	"""Helper that returns comments for a patch.
  Args:
    request: Django Request object.
  Returns:
    A 2-tuple of (old, new) where old/new are dictionaries that holds comments
      for that file, mapping from line number to a Comment entity.
  """
	old_dict = {}
	new_dict = {}
	query = models.Comment.query(models.Comment.patch_key == request.patch.key).order(models.Comment.date)
	for comment in query:
		if comment.draft and comment.author != request.user:
			continue
		comment.complete()
		if comment.left:
			dct = old_dict
		else:
			dct = new_dict
		dct.setdefault(comment.lineno, []).append(comment)
	return old_dict, new_dict
def _RenderDiffTableRows(request, old_lines, chunks, patch, colwidth=settings.DEFAULT_COLUMN_WIDTH, debug=False):
	"""Internal version of RenderDiffTableRows().
  Args:
    The same as for RenderDiffTableRows.
  Yields:
    Tuples (tag, row) where tag is an indication of the row type.
  """
	old_dict = {}
	new_dict = {}
	if patch:
		old_dict, new_dict = _GetComments(request)
	old_max, new_max = _ComputeLineCounts(old_lines, chunks)
	return _TableRowGenerator(patch, old_dict, old_max, "old", patch, new_dict, new_max, "new", patching.PatchChunks(old_lines, chunks), colwidth, debug, request)
def _TableRowGenerator(old_patch, old_dict, old_max, old_snapshot, new_patch, new_dict, new_max, new_snapshot, triple_iterator, colwidth=settings.DEFAULT_COLUMN_WIDTH, debug=False, request=None):
	"""Helper function to render side-by-side table rows.
  Args:
    old_patch: First models.Patch instance.
    old_dict: Dictionary with line numbers as keys and comments as values (left)
    old_max: Line count of the patch on the left.
    old_snapshot: A tag used in the comments form.
    new_patch: Second models.Patch instance.
    new_dict: Same as old_dict, but for the right side.
    new_max: Line count of the patch on the right.
    new_snapshot: A tag used in the comments form.
    triple_iterator: Iterator that yields (tag, old, new) triples.
    colwidth: Optional column width (default 80).
    debug: Optional debugging flag (default False).
  Yields:
    Tuples (tag, row) where tag is an indication of the row type and
    row is an HTML fragment representing one or more <td> elements.
  """
	diff_params = intra_region_diff.GetDiffParams(dbg=debug)
	ndigits = 1 + max(len(str(old_max)), len(str(new_max)))
	indent = 1 + ndigits
	old_offset = new_offset = 0
	row_count = 0
	if old_patch == new_patch and (old_max == 0 or new_max == 0):
		if old_max == 0:
			msg_old = "(Empty)"
		else:
			msg_old = ""
		if new_max == 0:
			msg_new = "(Empty)"
		else:
			msg_new = ""
		yield "", ('<tr><td class="info">%s</td>' '<td class="info">%s</td></tr>' % (msg_old, msg_new))
	elif old_patch is None or new_patch is None:
		msg_old = msg_new = ""
		if old_patch is None:
			msg_old = "(no file at all)"
		if new_patch is None:
			msg_new = "(no file at all)"
		yield "", ('<tr><td class="info">%s</td>' '<td class="info">%s</td></tr>' % (msg_old, msg_new))
	elif old_patch != new_patch and old_patch.lines == new_patch.lines:
		yield "", ('<tr><td class="info" colspan="2">' "(Both sides are equal)</td></tr>")
	for tag, old, new in triple_iterator:
		if tag.startswith("error"):
			yield "error", "<tr><td><h3>%s</h3></td></tr>\n" % cgi.escape(tag)
			return
		old1 = old_offset
		old_offset = old2 = old1 + len(old)
		new1 = new_offset
		new_offset = new2 = new1 + len(new)
		old_buff = []
		new_buff = []
		frag_list = []
		do_ir_diff = tag == "replace" and intra_region_diff.CanDoIRDiff(old, new)
		for i in xrange(max(len(old), len(new))):
			row_count += 1
			old_lineno = old1 + i + 1
			new_lineno = new1 + i + 1
			old_valid = old1 + i < old2
			new_valid = new1 + i < new2
			frags = []
			if i == 0 and tag != "equal":
				frags.append('<tr name="hook"')
			else:
				frags.append("<tr")
			frags.append(' id="pair-%d">' % row_count)
			old_intra_diff = ""
			new_intra_diff = ""
			if old_valid:
				old_intra_diff = old[i]
			if new_valid:
				new_intra_diff = new[i]
			frag_list.append(frags)
			if do_ir_diff:
				old_buff.append([old_valid, old_lineno, old_intra_diff])
				new_buff.append([new_valid, new_lineno, new_intra_diff])
			else:
				old_intra_diff = intra_region_diff.Break(old_intra_diff, 0, colwidth, "\n" + " " * indent)
				new_intra_diff = intra_region_diff.Break(new_intra_diff, 0, colwidth, "\n" + " " * indent)
				old_buff_out = [[old_valid, old_lineno, (old_intra_diff, True, None)]]
				new_buff_out = [[new_valid, new_lineno, (new_intra_diff, True, None)]]
				for tg, frag in _RenderDiffInternal(old_buff_out, new_buff_out, ndigits, tag, frag_list, do_ir_diff, old_dict, new_dict, old_patch, new_patch, old_snapshot, new_snapshot, debug, request):
					yield tg, frag
				frag_list = []
		if do_ir_diff:
			old_lines = [b[2] for b in old_buff]
			new_lines = [b[2] for b in new_buff]
			ret = intra_region_diff.IntraRegionDiff(old_lines, new_lines, diff_params)
			old_chunks, new_chunks, ratio = ret
			old_tag = "old"
			new_tag = "new"
			old_diff_out = intra_region_diff.RenderIntraRegionDiff(old_lines, old_chunks, old_tag, ratio, limit=colwidth, indent=indent, mark_tabs=True, dbg=debug)
			new_diff_out = intra_region_diff.RenderIntraRegionDiff(new_lines, new_chunks, new_tag, ratio, limit=colwidth, indent=indent, mark_tabs=True, dbg=debug)
			for (i, b) in enumerate(old_buff):
				b[2] = old_diff_out[i]
			for (i, b) in enumerate(new_buff):
				b[2] = new_diff_out[i]
			for tg, frag in _RenderDiffInternal(old_buff, new_buff, ndigits, tag, frag_list, do_ir_diff, old_dict, new_dict, old_patch, new_patch, old_snapshot, new_snapshot, debug, request):
				yield tg, frag
			old_buff = []
			new_buff = []
def _RenderDiffInternal(old_buff, new_buff, ndigits, tag, frag_list, do_ir_diff, old_dict, new_dict, old_patch, new_patch, old_snapshot, new_snapshot, debug, request):
	"""Helper for _TableRowGenerator()."""
	obegin = intra_region_diff.BEGIN_TAG % intra_region_diff.COLOR_SCHEME["old"]["match"]
	nbegin = intra_region_diff.BEGIN_TAG % intra_region_diff.COLOR_SCHEME["new"]["match"]
	oend = intra_region_diff.END_TAG
	nend = oend
	user = auth_utils.get_current_user()
	for i in xrange(len(old_buff)):
		tg = tag
		old_valid, old_lineno, old_out = old_buff[i]
		new_valid, new_lineno, new_out = new_buff[i]
		old_intra_diff, old_has_newline, old_debug_info = old_out
		new_intra_diff, new_has_newline, new_debug_info = new_out
		frags = frag_list[i]
		frags.append(_RenderDiffColumn(old_valid, tag, ndigits, old_lineno, obegin, oend, old_intra_diff, do_ir_diff, old_has_newline, "old"))
		frags.append(_RenderDiffColumn(new_valid, tag, ndigits, new_lineno, nbegin, nend, new_intra_diff, do_ir_diff, new_has_newline, "new"))
		frags.append("</tr>\n")
		if debug:
			frags.append("<tr>")
			if old_debug_info:
				frags.append('<td class="debug-info">%s</td>' % old_debug_info.replace("\n", "<br>"))
			else:
				frags.append("<td></td>")
			if new_debug_info:
				frags.append('<td class="debug-info">%s</td>' % new_debug_info.replace("\n", "<br>"))
			else:
				frags.append("<td></td>")
			frags.append("</tr>\n")
		if old_patch or new_patch:
			if (old_valid and old_lineno in old_dict) or (new_valid and new_lineno in new_dict):
				tg += "_comment"
				frags.append('<tr class="inline-comments" name="hook">')
			else:
				frags.append('<tr class="inline-comments">')
			frags.append(_RenderInlineComments(old_valid, old_lineno, old_dict, user, old_patch, old_snapshot, "old", request))
			frags.append(_RenderInlineComments(new_valid, new_lineno, new_dict, user, new_patch, new_snapshot, "new", request))
			frags.append("</tr>\n")
		yield tg, "".join(frags)
def _RenderDiffColumn(line_valid, tag, ndigits, lineno, begin, end, intra_diff, do_ir_diff, has_newline, prefix):
	"""Helper function for _RenderDiffInternal().
  Returns:
    A rendered column.
  """
	if line_valid:
		cls_attr = "%s%s" % (prefix, tag)
		if tag == "equal":
			lno = "%*d" % (ndigits, lineno)
		else:
			lno = _MarkupNumber(ndigits, lineno, "u")
		if tag == "replace":
			col_content = "%s%s %s%s" % (begin, lno, end, intra_diff)
			if not do_ir_diff or not has_newline:
				cls_attr = cls_attr + "1"
		else:
			col_content = "%s %s" % (lno, intra_diff)
		return '<td class="%s" id="%scode%d">%s</td>' % (cls_attr, prefix, lineno, col_content)
	else:
		return '<td class="%sblank"></td>' % prefix
def _RenderInlineComments(line_valid, lineno, data, user, patch, snapshot, prefix, request):
	"""Helper function for _RenderDiffInternal().
  Returns:
    Rendered comments.
  """
	comments = []
	if line_valid:
		comments.append('<td id="%s-line-%s">' % (prefix, lineno))
		if lineno in data:
			patchset = patch.patchset_key.get()
			issue = patchset.issue_key.get()
			comments.append(_ExpandTemplate("inline_comment.html", request, user=user, patch=patch, patchset=patchset, issue=issue, snapshot=snapshot, side="a" if prefix == "old" else "b", comments=data[lineno], lineno=lineno))
		comments.append("</td>")
	else:
		comments.append("<td></td>")
	return "".join(comments)
def RenderUnifiedTableRows(request, parsed_lines):
	"""Render the HTML table rows for a unified diff for a patch.
  Args:
    request: Django Request object.
    parsed_lines: List of tuples for each line that contain the line number,
      if they exist, for the old and new file.
  Returns:
    A list of html table rows.
  """
	old_dict, new_dict = _GetComments(request)
	rows = []
	for old_line_no, new_line_no, line_text in parsed_lines:
		row1_id = row2_id = ""
		if old_line_no:
			row1_id = 'id="oldcode%d"' % old_line_no
			row2_id = 'id="old-line-%d"' % old_line_no
		elif new_line_no:
			row1_id = 'id="newcode%d"' % new_line_no
			row2_id = 'id="new-line-%d"' % new_line_no
		if line_text[0] == "+":
			style = "udiffadd"
		elif line_text[0] == "-":
			style = "udiffremove"
		else:
			style = ""
		rows.append('<tr><td class="udiff %s" %s>%s</td></tr>' % (style, row1_id, cgi.escape(line_text)))
		frags = []
		if old_line_no in old_dict or new_line_no in new_dict:
			frags.append('<tr class="inline-comments" name="hook">')
			if old_line_no in old_dict:
				dct = old_dict
				line_no = old_line_no
				snapshot = "old"
			else:
				dct = new_dict
				line_no = new_line_no
				snapshot = "new"
			frags.append(_RenderInlineComments(True, line_no, dct, request.user, request.patch, snapshot, snapshot, request))
		else:
			frags.append('<tr class="inline-comments">')
			frags.append("<td " + row2_id + "></td>")
		frags.append("</tr>")
		rows.append("".join(frags))
	return rows
def _ComputeLineCounts(old_lines, chunks):
	"""Compute the length of the old and new sides of a diff.
  Args:
    old_lines: List of lines representing the original file.
    chunks: List of chunks as returned by patching.ParsePatchToChunks().
  Returns:
    A tuple (old_len, new_len) representing len(old_lines) and
    len(new_lines), where new_lines is the list representing the
    result of applying the patch chunks to old_lines, however, without
    actually computing new_lines.
  """
	old_len = len(old_lines)
	new_len = old_len
	if chunks:
		(_, old_b), (_, new_b), old_lines, _ = chunks[-1]
		new_len += new_b - old_b
	return old_len, new_len
def _MarkupNumber(ndigits, number, tag):
	"""Format a number in HTML in a given width with extra markup.
  Args:
    ndigits: the total width available for formatting
    number: the number to be formatted
    tag: HTML tag name, e.g. 'u'
  Returns:
    An HTML string that displays as ndigits wide, with the
    number right-aligned and surrounded by an HTML tag; for example,
    _MarkupNumber(42, 4, 'u') returns '  <u>42</u>'.
  """
	formatted_number = str(number)
	space_prefix = " " * (ndigits - len(formatted_number))
	return "%s<%s>%s</%s>" % (space_prefix, tag, formatted_number, tag)
def _ExpandTemplate(name, request, **params):
	"""Wrapper around django.template.loader.render_to_string().
  For convenience, this takes keyword arguments instead of a dict.
  """
	rslt = loader.render_to_string(name, params, context_instance=RequestContext(request))
	return rslt.encode("utf-8")