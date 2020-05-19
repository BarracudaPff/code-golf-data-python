from __future__ import unicode_literals
import logging
import os
import re
import shutil
import tempfile
from django.core.exceptions import ValidationError
from django.utils import six
from django.utils.encoding import force_text
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.translation import ugettext as _
from djblets.util.filesystem import is_exe_in_path
from reviewboard.scmtools.core import SCMTool, HEAD, PRE_CREATION
from reviewboard.scmtools.errors import AuthenticationError, SCMError, FileNotFoundError, RepositoryNotFoundError
from reviewboard.diffviewer.parser import DiffParser, DiffParserError
from reviewboard.ssh import utils as sshutils
from reviewboard.ssh.errors import SSHAuthenticationError, SSHError
sshutils.register_rbssh("CVS_RSH")
class CVSTool(SCMTool):
	name = "CVS"
	diffs_use_absolute_paths = True
	field_help_text = {"path": "The CVSROOT used to access the repository."}
	dependencies = {"executables": ["cvs"]}
	rev_re = re.compile(br"^.*?(\d+(\.\d+)+)\r?$")
	remote_cvsroot_re = re.compile(r"^(:(?P<protocol>[gkp]?server|ext|ssh|extssh):" r"((?P<username>[^:@]+)(:(?P<password>[^@]+))?@)?)?" r"(?P<hostname>[^:]+):(?P<port>\d+)?(?P<path>.*)")
	local_cvsroot_re = re.compile(r"^:(?P<protocol>local|fork):(?P<path>.+)")
	def __init__(self, repository):
		super(CVSTool, self).__init__(repository)
		credentials = repository.get_credentials()
		self.cvsroot, self.repopath = self.build_cvsroot(self.repository.path, credentials["username"], credentials["password"], validate=False)
		local_site_name = None
		if repository.local_site:
			local_site_name = repository.local_site.name
		self.client = CVSClient(self.cvsroot, self.repopath, local_site_name)
	def get_file(self, path, revision=HEAD, **kwargs):
		if not path:
			raise FileNotFoundError(path, revision)
		return self.client.cat_file(path, revision)
	def parse_diff_revision(self, filename, revision, *args, **kwargs):
		"""Parse and return a filename and revision from a diff.
        Args:
            filename (bytes):
                The filename as represented in the diff.
            revision (bytes):
                The revision as represented in the diff.
            *args (tuple, unused):
                Unused positional arguments.
            **kwargs (dict, unused):
                Unused keyword arguments.
        Returns:
            tuple:
            A tuple containing two items:
            1. The normalized filename as a byte string.
            2. The normalized revision as a byte string or a
               :py:class:`~reviewboard.scmtools.core.Revision`.
        """
		assert isinstance(filename, bytes), "filename must be a byte string, not %r" % type(filename)
		assert isinstance(revision, bytes), "revision must be a byte string, not %r" % type(revision)
		if revision == b"PRE-CREATION":
			return filename, PRE_CREATION
		m = self.rev_re.match(revision)
		if m:
			return filename, m.group(1)
		colon_idx = filename.rfind(b":")
		if colon_idx == -1:
			raise SCMError("Unable to parse diff revision header " '(file_str="%s", revision_str="%s")' % (filename.decode("utf-8"), revision.decode("utf-8")))
		return filename[:colon_idx], filename[colon_idx + 1 :]
	def get_parser(self, data):
		return CVSDiffParser(data, self.repopath)
	def normalize_path_for_display(self, filename):
		"""Normalize a path from a diff for display to the user.
        This can take a path/filename found in a diff and normalize it,
        stripping away unwanted information, so that it displays in a better
        way in the diff viewer.
        For CVS, this strips trailing ",v" from filenames.
        Args:
            filename (unicode):
                The filename/path to normalize.
        Returns:
            unicode:
            The resulting filename/path.
        """
		return re.sub(",v$", "", filename)
	def normalize_patch(self, patch, filename, revision=HEAD):
		"""Normalizes the content of a patch.
        This will collapse any keywords in the patch, ensuring that we can
        safely compare them against any files we cat from the repository,
        without the keyword values conflicting.
        """
		return self.client.collapse_keywords(patch)
	@classmethod
	def build_cvsroot(cls, cvsroot, username, password, validate=True):
		"""Parse and construct a CVSROOT from the given arguments.
        This will take a repository path or CVSROOT provided by the caller,
        optionally validate it, and return both a new CVSROOT and the path
        within it.
        If a username/password are provided as arguments, but do not exist in
        ``cvsroot``, then the resulting CVSROOT will contain the
        username/password.
        If data is provided that is not supported by the type of protocol
        specified in ``cvsroot``, then it will raise a
        :py:class:`~django.core.exceptions.ValidationError` (if validating)
        or strip the data from the CVSROOT.
        Args:
            cvsroot (unicode):
                A CVSROOT string, or a bare repository path to turn into one.
            username (unicode):
                Optional username for the CVSROOT.
            password (unicode):
                Optional password for the CVSROOT (only supported for
                ``pserver`` types).
            validate (bool, optional):
                Whether to validate the provided CVSROOT and username/password.
                If set, and the resulting CVSROOT would be invalid, then an
                error is raised.
                If not set, the resulting CVSROOT will have the invalid data
                stripped.
                This will check for ports, usernames, and passwords, depending
                on the type of CVSROOT provided.
        Returns:
            unicode:
            The resulting validated CVSROOT.
        Raises:
            django.core.exceptions.ValidationError:
                The provided data had a validation error. This is only raised
                if ``validate`` is set.
        """
		m = cls.remote_cvsroot_re.match(cvsroot)
		if m:
			protocol = m.group("protocol") or "pserver"
			username = m.group("username") or username
			password = m.group("password") or password
			port = m.group("port") or None
			path = m.group("path")
			if password and protocol != "pserver":
				if validate:
					raise ValidationError(_('"%s" CVSROOTs do not support passwords.') % protocol)
				password = None
			if port and protocol not in ("pserver", "gserver", "kserver"):
				if validate:
					raise ValidationError(_('"%s" CVSROOTs do not support specifying ports.') % protocol)
				port = None
			if username:
				if password:
					credentials = "%s:%s@" % (username, password)
				else:
					credentials = "%s@" % (username)
			else:
				credentials = ""
			cvsroot = ":%s:%s%s:%s%s" % (protocol, credentials, m.group("hostname"), port or "", path)
		else:
			m = cls.local_cvsroot_re.match(cvsroot)
			if m:
				path = m.group("path")
				if validate:
					if username:
						raise ValidationError(_('"%s" CVSROOTs do not support usernames.') % m.group("protocol"))
					if password:
						raise ValidationError(_('"%s" CVSROOTs do not support passwords.') % m.group("protocol"))
			else:
				path = cvsroot
		return cvsroot, path
	@classmethod
	def check_repository(cls, path, username=None, password=None, local_site_name=None):
		"""
        Performs checks on a repository to test its validity.
        This should check if a repository exists and can be connected to.
        This will also check if the repository requires an HTTPS certificate.
        The result is returned as an exception. The exception may contain
        extra information, such as a human-readable description of the problem.
        If the repository is valid and can be connected to, no exception
        will be thrown.
        """
		try:
			cvsroot, repopath = cls.build_cvsroot(path, username, password)
		except ValidationError as e:
			raise SCMError("; ".join(e.messages))
		m = cls.remote_cvsroot_re.match(path)
		if m and m.group("protocol") in ("ext", "ssh", "extssh"):
			try:
				sshutils.check_host(m.group("hostname"), username, password, local_site_name)
			except SSHAuthenticationError as e:
				raise AuthenticationError(e.allowed_types, six.text_type(e), e.user_key)
			except:
				raise
		client = CVSClient(cvsroot, repopath, local_site_name)
		try:
			client.check_repository()
		except (AuthenticationError, SCMError):
			raise
		except (SSHError, FileNotFoundError):
			raise RepositoryNotFoundError()
	@classmethod
	def parse_hostname(cls, path):
		"""Parses a hostname from a repository path."""
		return urlparse(path)[1]
class CVSDiffParser(DiffParser):
	"""Diff parser for CVS diff files.
    This handles parsing diffs generated by :command:`cvs diff`, extracting
    the diff content and normalizing filenames for proper display in the
    diff viewer.
    """
	def __init__(self, data, rel_repo_path):
		super(CVSDiffParser, self).__init__(data)
		self.rcs_file_re = re.compile(br"^RCS file: (%s/)?(?P<path>.+?)(,v)?$" % re.escape(rel_repo_path.encode("utf-8")))
		self.binary_re = re.compile(br"^Binary files (?P<origFile>.+) and (?P<newFile>.+) differ$")
	def parse_special_header(self, linenum, info):
		linenum = super(CVSDiffParser, self).parse_special_header(linenum, info)
		if "index" not in info:
			return linenum
		m = self.rcs_file_re.match(self.lines[linenum])
		if m:
			info["filename"] = m.group("path")
			linenum += 1
		else:
			raise DiffParserError("Unable to find RCS line", linenum)
		while self.lines[linenum].startswith(b"retrieving "):
			linenum += 1
		if self.lines[linenum].startswith(b"diff "):
			linenum += 1
		return linenum
	def parse_diff_header(self, linenum, info):
		linenum = super(CVSDiffParser, self).parse_diff_header(linenum, info)
		if "origFile" not in info:
			m = self.binary_re.match(self.lines[linenum])
			if m:
				info["binary"] = True
				info["origFile"] = m.group("origFile")
				info["newFile"] = info.get("filename") or m.group("newFile")
				info["origInfo"] = b""
				info["newInfo"] = b""
				linenum += 1
		if info.get("origFile") in (b"/dev/null", b"nul:"):
			info["origFile"] = info["newFile"]
			info["origInfo"] = PRE_CREATION
		elif "filename" in info:
			if info.get("newFile") == info.get("origFile"):
				info["newFile"] = info["filename"]
			info["origFile"] = info["filename"]
		if info.get("newFile") == b"/dev/null":
			info["deleted"] = True
		return linenum
	def normalize_diff_filename(self, filename):
		"""Normalize filenames in diffs.
        The default behavior of stripping off leading slashes doesn't work for
        CVS, so this overrides it to just return the filename un-molested.
        """
		return filename
class CVSClient(object):
	keywords = [b"Author", b"Date", b"Header", b"Id", b"Locker", b"Name", b"RCSfile", b"Revision", b"Source", b"State"]
	def __init__(self, cvsroot, path, local_site_name):
		self.tempdir = None
		self.currentdir = os.getcwd()
		self.cvsroot = cvsroot
		self.path = path
		self.local_site_name = local_site_name
		if not is_exe_in_path("cvs"):
			raise ImportError
	def cleanup(self):
		if self.currentdir != os.getcwd():
			os.chdir(self.currentdir)
			if self.tempdir:
				shutil.rmtree(self.tempdir)
	def cat_file(self, filename, revision):
		repos_path = self.path.split(":")[-1]
		if "@" in repos_path:
			repos_path = "/" + repos_path.split("@")[-1].split("/", 1)[-1]
		if filename.startswith(repos_path + "/"):
			filename = filename[len(repos_path) + 1 :]
		if filename.endswith(",v"):
			filename = filename[:-2]
		filenameAttic = filename
		if "/Attic/" in filename:
			filename = "/".join(filename.rsplit("/Attic/", 1))
		elif "\\Attic\\" in filename:
			filename = "\\".join(filename.rsplit("\\Attic\\", 1))
		elif "\\" in filename:
			pos = filename.rfind("\\")
			filenameAttic = filename[0:pos] + "\\Attic" + filename[pos:]
		elif "/" in filename:
			pos = filename.rfind("/")
			filenameAttic = filename[0:pos] + "/Attic" + filename[pos:]
		else:
			filenameAttic = None
		try:
			return self._cat_specific_file(filename, revision)
		except FileNotFoundError:
			if filenameAttic:
				return self._cat_specific_file(filenameAttic, revision)
			else:
				raise
	def _cat_specific_file(self, filename, revision):
		self.tempdir = tempfile.mkdtemp()
		os.chdir(self.tempdir)
		p = SCMTool.popen(["cvs", "-f", "-d", self.cvsroot, "checkout", "-kk", "-r", six.text_type(revision), "-p", filename], self.local_site_name)
		contents = p.stdout.read()
		errmsg = force_text(p.stderr.read())
		failure = p.wait()
		if not errmsg or errmsg.startswith("cvs checkout: cannot find module") or errmsg.startswith("cvs checkout: could not read RCS file"):
			self.cleanup()
			raise FileNotFoundError(filename, revision)
		if (failure and not errmsg.startswith("==========")) and ".cvspass does not exist - creating new file" not in errmsg:
			self.cleanup()
			raise SCMError(errmsg)
		self.cleanup()
		return contents
	def check_repository(self):
		p = SCMTool.popen(["cvs", "-f", "-d", self.cvsroot, "version"], self.local_site_name)
		errmsg = six.text_type(p.stderr.read())
		if p.wait() != 0:
			logging.error("CVS repository validation failed for " "CVSROOT %s: %s", self.cvsroot, errmsg)
			auth_failed_prefix = "cvs version: authorization failed: "
			for line in errmsg.splitlines():
				if line.startswith(auth_failed_prefix):
					raise AuthenticationError(msg=line[len(auth_failed_prefix) :].strip())
			raise SCMError(errmsg)
	def collapse_keywords(self, data):
		"""Collapse CVS/RCS keywords in string.
        CVS allows for several keywords (such as ``$Id$`` and ``$Revision$``)
        to be expanded, though these keywords are limited to a fixed set
        (and associated aliases) and must be enabled per-file.
        When we cat a file on CVS, the keywords come back collapsed, but
        the diffs uploaded may have expanded keywords. We use this function
        to collapse them back down in order to be able to apply the patch.
        Args:
            data (bytes):
                The file contents.
        Return:
            bytes:
            The resulting file contents with all keywords collapsed.
        """
		return re.sub(br"\$(%s):([^\$\n\r]*)\$" % b"|".join(self.keywords), br"$\1$", data, flags=re.IGNORECASE)