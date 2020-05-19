"""Signal handlers."""
def on_users_changed(instance, action, pk_set, reverse, **kwargs):
	"""Handle the users of a Local Site changing.
    This method ensures that any
    :py:class:`Applications <reviewboard.oauth.models.Application>` owned by
    users removed from a a :py:class:`~reviewboard.site.models.LocalSite` will
    be re-assigned to an administrator on that Local Site and disabled so the
    client secret can be changed.
    Args:
        instance (django.contrib.auth.models.User or
                  reviewboard.reviews.models.review_group.Group):
            The model that changed.
        action (unicode):
            The change action on the Local Site.
        pk_set (list of int):
            The primary keys of the objects changed.
        reverse (bool):
            Whether or not the relation or the reverse relation is changing.
        **kwargs (dict):
            Ignored arguments from the signal.
    """
	users = None
	if action == "post_remove":
		if reverse:
			users = [instance]
		else:
			users = list(User.objects.filter(pk__in=pk_set))
	elif action == "pre_clear":
		if reverse:
			users = [instance]
		else:
			users = list(instance.users.all())
	if not users:
		return
	applications = list(Application.objects.filter(user__in=users, local_site__isnull=False).prefetch_related("local_site__admins"))
	if not applications:
		return
	users_by_pk = {user.pk: user for user in users}
	for application in applications:
		user = users_by_pk[application.user_id]
		if not application.local_site.is_accessible_by(user):
			application.enabled = False
			application.user = application.local_site.admins.first()
			application.original_user = user
			application.save(update_fields=["enabled", "original_user", "user"])