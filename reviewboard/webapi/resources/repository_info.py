class RepositoryInfoResource(WebAPIResource):
	"""Provides server-side information on a repository.
    Some repositories can return custom server-side information.
    This is not available for all types of repositories. The information
    will be specific to that type of repository.
    """
	name = "info"
	policy_id = "repository_info"
	singleton = True
	allowed_methods = ("GET",)
	mimetype_item_resource_name = "repository-info"
	@webapi_check_local_site
	@webapi_check_login_required
	@webapi_response_errors(DOES_NOT_EXIST, REPO_NOT_IMPLEMENTED, REPO_INFO_ERROR)
	def get(self, request, *args, **kwargs):
		"""Returns repository-specific information from a server."""
		try:
			repository = resources.repository.get_object(request, *args, **kwargs)
		except ObjectDoesNotExist:
			return DOES_NOT_EXIST
		try:
			tool = repository.get_scmtool()
			return 200, {self.item_result_key: tool.get_repository_info()}
		except NotImplementedError:
			return REPO_NOT_IMPLEMENTED
		except AuthenticationError as e:
			return REPO_INFO_ERROR.with_message(six.text_type(e))
		except:
			return REPO_INFO_ERROR
repository_info_resource = RepositoryInfoResource()