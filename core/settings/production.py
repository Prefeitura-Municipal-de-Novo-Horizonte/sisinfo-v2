"""
Configurações específicas para produção.
"""
from decouple import Csv, config
from dj_database_url import parse as dburl

from core.settings.base import *

DEBUG = False
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())
EMAIL_BACKEND = config("EMAIL_BACKEND")
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DATABASES = {
    "default": dburl(config("DATABASE_URL"))
}
# Configurações de segurança recomendadas
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging específico para produção
LOG_LEVEL = config("LOG_LEVEL")
LOGGING["root"]["level"] = LOG_LEVEL
LOGGING["loggers"]["django"]["level"] = LOG_LEVEL
# Handler de e-mail para admins
LOGGING["handlers"]["mail_admins"] = {
    "level": "ERROR",
    "class": "django.utils.log.AdminEmailHandler",
    "formatter": "verbose",
}
LOGGING["loggers"]["django"]["handlers"].append("mail_admins")

# Configurar ADMINS e SERVER_EMAIL para envio de erros críticos
ADMINS = [("Prefeitura Municipal de Novo Horizonte",
           "suporte@novohorizonte.sp.gov.br")]
SERVER_EMAIL = "suporte@novohorizonte.sp.gov.br"
