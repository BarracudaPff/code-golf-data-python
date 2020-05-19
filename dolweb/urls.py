admin.autodiscover()
urlpatterns = [url(r"^$", home, name="home"), url(r"^media/", include("dolweb.media.urls")), url(r"^docs/", include("dolweb.docs.urls")), url(r"^download/", include("dolweb.downloads.urls")), url(r"^blog/", include("dolweb.blog.urls")), url(r"^compat/", include("dolweb.compat.urls")), url(r"^admin/", admin.site.urls), url(r"^mgmt/(?P<cmd>.+)$", run_command, name="mgmt_run_command"), url(r"^update/", include("dolweb.update.urls"))]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
	urlpatterns += [url(r"^__debug__/", include(debug_toolbar.urls))]