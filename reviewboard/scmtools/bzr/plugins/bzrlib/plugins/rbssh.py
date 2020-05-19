"""rbssh plugin for Bazaar.
This registers :command:`rbssh` as a SSH plugin for Bazaar. It's run entirely
outside of the Review Board process, and is invoked exclusively by
:command:`bzr`.
"""
class RBSSHVendor(SubprocessVendor):
	"""SSH vendor class for using rbssh."""
	executable_path = "rbssh"
	def _get_vendor_specific_argv(self, username, host, port=None, subsystem=None, command=None):
		"""Return arguments to pass to rbssh.
        Args:
            username (unicode):
                The username to connect with.
            host (unicode):
                The hostname to connect to.
            port (int, optional):
                The custom port to connect to.
            subsystem (unicode, optional):
                The SSH subsystem to use.
            command (unicode, optional):
                The command to invoke through the SSH connection.
        Returns:
            list of unicode:
            The list of arguments to pass to :command:`rbssh`.
        """
		args = [self.executable_path]
		if port is not None:
			args.extend(["-p", six.text_type(port)])
		if username is not None:
			args.extend(["-l", username])
		if subsystem is not None:
			args.extend(["-s", host, subsystem])
		else:
			args.extend([host] + command)
		return args
vendor = RBSSHVendor()
register_ssh_vendor("rbssh", vendor)
register_default_ssh_vendor(vendor)