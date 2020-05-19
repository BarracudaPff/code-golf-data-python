DEBUG = False
TEMPLATE_DEBUG = False
DATABASES = settings.DATABASES
DATABASES["default"] = dj_database_url.config()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
ALLOWED_HOSTS = ["*"]
SHARE_URL = "http://launchwithcode.com/?ref="