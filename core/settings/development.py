"""
Configurações específicas para desenvolvimento.
"""
from decouple import config
from dj_database_url import parse as dburl

from .base import *

DEBUG = True
SECRET_KEY = config("SECRET_KEY", default="dev-secret-key")
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DATABASES = {
    "default": dburl(config("DATABASE_URL", default="sqlite:///db.sqlite3"))
}
