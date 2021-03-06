@staff_member_required
def dashboard(request, template_name="admin/dashboard.html"):
	"""Display the administration dashboard.
    This is the entry point to the admin site, containing news updates and
    useful administration tasks.
    """
	profile = request.user.get_profile()
	profile_data = profile.extra_data
	selected_primary_widgets, unselected_primary_widgets = _get_widget_selections(primary_widgets, profile_data.get("primary_widget_selections"))
	selected_secondary_widgets, unselected_secondary_widgets = _get_widget_selections(secondary_widgets, profile_data.get("secondary_widget_selections"))
	sorted_primary_widgets = _sort_widgets(selected_primary_widgets, profile_data.get("primary_widget_positions"))
	sorted_secondary_widgets = _sort_widgets(selected_secondary_widgets, profile_data.get("secondary_widget_positions"))
	return render(request=request, template_name=template_name, context={"primary_widgets": primary_widgets, "root_path": reverse("admin:index"), "secondary_widgets": secondary_widgets, "selected_primary_widgets": sorted_primary_widgets, "selected_secondary_widgets": sorted_secondary_widgets, "support_data": serialize_support_data(request, True), "title": _("Admin Dashboard"), "unselected_primary_widgets": unselected_primary_widgets, "unselected_secondary_widgets": unselected_secondary_widgets})
def _get_widget_selections(widgets, widget_selections):
	"""Return lists of widgets that are selected and unselected.
    Args:
        widgets (list):
            A list of widgets that we have registered already.
        widget_selections (dict):
            A dictionary mapping widgets
            (:py:class:`reviewboard.admin.widgets.Widget`) to whether or not
            they are selected (as a :py:class:`unicode`).
    Returns:
        tuple of list:
        A 2-tuple containing a list of selected widgets (to display
        on the dashboard) and a list of the unselected widgets.
    """
	selected_widgets = []
	unselected_widgets = []
	if widget_selections:
		for widget in widgets:
			if widget_selections.get(widget.widget_id) == "1":
				selected_widgets.append(widget)
			else:
				unselected_widgets.append(widget)
	else:
		selected_widgets = widgets
		unselected_widgets = None
	return selected_widgets, unselected_widgets
def _sort_widgets(selected_widgets, widget_positions):
	"""Sort widgets based on their positions.
    Args:
        selected_widgets (list):
            A list of widgets that we have selected to display.
        widget_positions (dict):
            A dictionary mapping widget IDs to their ordinals.
    Returns:
        list:
        A list of sorted widgets.
    """
	if widget_positions:
		sorted_widgets = sorted(selected_widgets, key=lambda widget: widget_positions.get(widget.widget_id, len(widget_positions)))
	else:
		sorted_widgets = selected_widgets
	return sorted_widgets
@staff_member_required
def cache_stats(request, template_name="admin/cache_stats.html"):
	"""Display statistics on the cache.
    This includes such pieces of information as memory used, cache misses, and
    uptime.
    """
	cache_stats = get_cache_stats()
	cache_info = settings.CACHES[DEFAULT_FORWARD_CACHE_ALIAS]
	return render(request=request, template_name=template_name, context={"cache_hosts": cache_stats, "cache_backend": cache_info["BACKEND"], "title": _("Server Cache"), "root_path": reverse("admin:index")})
@staff_member_required
def security(request, template_name="admin/security.html"):
	"""Run security checks and report the results."""
	runner = SecurityCheckRunner()
	results = runner.run()
	return render(request=request, template_name=template_name, context={"test_results": results, "title": _("Security Checklist")})
@superuser_required
def site_settings(request, form_class, template_name="admin/settings.html"):
	"""Render the general site settings page."""
	return djblets_site_settings(request, form_class, template_name, {"root_path": reverse("admin:index")})
@csrf_protect
@superuser_required
def ssh_settings(request, template_name="admin/ssh_settings.html"):
	"""Render the SSH settings page."""
	client = SSHClient()
	key = client.get_user_key()
	if request.method == "POST":
		form = SSHSettingsForm(request.POST, request.FILES)
		if form.is_valid():
			if form.did_request_delete() and client.get_user_key() is not None:
				try:
					form.delete()
					return HttpResponseRedirect(".")
				except Exception as e:
					logging.error("Deleting SSH key failed: %s" % e)
			else:
				try:
					form.create(request.FILES)
					return HttpResponseRedirect(".")
				except Exception as e:
					logging.error("Uploading SSH key failed: %s" % e)
	else:
		form = SSHSettingsForm()
	if key:
		fingerprint = humanize_key(key)
	else:
		fingerprint = None
	return render(request=request, template_name=template_name, context={"key": key, "fingerprint": fingerprint, "public_key": client.get_public_key(key), "form": form})
def manual_updates_required(request, updates):
	"""Render a page showing required updates that the admin must make.
    Args:
        request (django.http.HttpRequest):
            The HTTP request from the client.
        updates (list):
            The list of required updates to display on the page.
    Returns:
        django.http.HttpResponse:
        The response to send to the client.
    """
	return render(request=request, template_name="admin/manual_updates_required.html", context={"updates": [render_to_string(template_name=update_template_name, context=extra_context, request=request) for update_template_name, extra_context in updates]})
def widget_move(request):
	"""Handle moving of admin widgets.
    This will update the saved position of the admin widgets based on a user's
    activity in the dashboard.
    """
	profile = request.user.get_profile()
	profile_data = profile.extra_data
	widget_type = request.POST.get("type")
	if widget_type == "primary":
		positions_key = "primary_widget_positions"
		widgets = primary_widgets
	else:
		positions_key = "secondary_widget_positions"
		widgets = secondary_widgets
	positions = profile_data.setdefault(positions_key, {})
	for widget in widgets:
		widget_position = request.POST.get(widget.widget_id)
		if widget_position is not None:
			positions[widget.widget_id] = widget_position
		else:
			positions[widget.widget_id] = str(len(widgets))
	profile.save(update_fields=("extra_data",))
	return HttpResponse()
def widget_select(request):
	"""Handle selection of admin widgets.
    This will enable or disable widgets based on a user's activity in the
    dashboard.
    """
	profile = request.user.get_profile()
	profile_data = profile.extra_data
	widget_type = request.POST.get("type")
	if widget_type == "primary":
		selections_key = "primary_widget_selections"
		widgets = primary_widgets
	else:
		selections_key = "secondary_widget_selections"
		widgets = secondary_widgets
	initial_selections = {}
	for widget in widgets:
		initial_selections[widget.widget_id] = "1"
	selections = profile_data.setdefault(selections_key, initial_selections)
	for widget in widgets:
		widget_selection = request.POST.get(widget.widget_id)
		if widget_selection is not None:
			selections[widget.widget_id] = widget_selection
	profile.save(update_fields=("extra_data",))
	return HttpResponse()
def widget_activity(request):
	"""Return JSON data for the admin activity widget."""
	activity_data = dynamic_activity_data(request)
	return HttpResponse(json.dumps(activity_data), content_type="application/json")
def support_redirect(request, **kwargs):
	"""Return an HttpResponseRedirect to the Beanbag support page."""
	return HttpResponseRedirect(get_support_url(request))