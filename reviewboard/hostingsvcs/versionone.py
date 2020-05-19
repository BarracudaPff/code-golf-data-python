class VersionOneForm(HostingServiceForm):
	versionone_url = forms.CharField(label=_("VersionOne URL"), max_length=64, required=True, widget=forms.TextInput(attrs={"size": "60"}), validators=[validate_bug_tracker_base_hosting_url])
class VersionOne(HostingService):
	name = "VersionOne"
	form = VersionOneForm
	bug_tracker_field = "%(versionone_url)s/assetdetail.v1?Number=%%s"
	supports_bug_trackers = True