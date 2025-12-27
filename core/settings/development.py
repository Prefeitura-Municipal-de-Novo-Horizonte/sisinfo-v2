"""
Configurações específicas para desenvolvimento.
"""
from decouple import Csv, config
from dj_database_url import parse as dburl

from core.settings.base import *

DEBUG = True
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())
EMAIL_BACKEND = config("EMAIL_BACKEND", default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config("EMAIL_HOST", default='localhost')
EMAIL_PORT = config("EMAIL_PORT", default=25, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=False, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default='')
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default='')

# Supabase NON_POOLING para dev (porta 5432), fallback para POSTGRES_URL ou DATABASE_URL
DATABASE_URL = config(
    "POSTGRES_URL_NON_POOLING",
    default=config("POSTGRES_URL", default=config("DATABASE_URL", default=""))
)
DATABASES = {
    "default": dburl(DATABASE_URL)
}

# Browserless.io API Key for PDF generation
BROWSERLESS_API_KEY = config("BROWSERLESS_API_KEY", default="")

# Logging específico para desenvolvimento
# LOG_LEVEL = "DEBUG"
# LOGGING["root"]["level"] = LOG_LEVEL
# LOGGING["loggers"]["django"]["level"] = LOG_LEVEL
