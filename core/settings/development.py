"""
Configurações específicas para desenvolvimento.
"""
from decouple import Csv, config
from dj_database_url import parse as dburl

from core.settings.base import *

DEBUG = True
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    "default": dburl(config("DATABASE_URL"))
}

# Logging específico para desenvolvimento
LOG_LEVEL = "DEBUG"
LOGGING["root"]["level"] = LOG_LEVEL
LOGGING["loggers"]["django"]["level"] = LOG_LEVEL
