"""
WSGI config for django_react_sample project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_react_sample.settings")
application = get_wsgi_application()