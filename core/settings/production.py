"""
Configurações específicas para produção.
"""
import re
from decouple import Csv, config
from dj_database_url import parse as dburl

from core.settings.base import *


def clean_supabase_url(url: str) -> str:
    """
    Remove parâmetros inválidos da URL do Supabase.
    A integração Vercel+Supabase adiciona 'supa=base-pooler.x' que o psycopg2 não reconhece.
    """
    if not url:
        return url
    # Remove &supa=... ou ?supa=...
    url = re.sub(r'[&?]supa=[^&]*', '', url)
    # Se ficou com ? no final sem parâmetros, adiciona sslmode
    if url.endswith('?'):
        url = url[:-1]
    return url


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

# Supabase usa POSTGRES_URL, fallback para DATABASE_URL (Aiven/legacy)
# Limpa parâmetros inválidos adicionados pela integração Vercel
DATABASE_URL = clean_supabase_url(
    config("POSTGRES_URL", default=config("DATABASE_URL", default=""))
)
DATABASES = {
    "default": {
        **dburl(DATABASE_URL),
        # IMPORTANTE: Em ambiente serverless (Vercel) com Supabase Pooler,
        # CONN_MAX_AGE deve ser 0 para evitar erro "cursor does not exist"
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": True,
        # Desabilita server-side cursors - necessário para PgBouncer Transaction Mode
        "DISABLE_SERVER_SIDE_CURSORS": True,
    }
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

# Redefinir LOGGING para ambiente serverless (Vercel)
LOG_LEVEL = config("LOG_LEVEL")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "mail_admins"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

# Browserless.io API Key for PDF generation
BROWSERLESS_API_KEY = config("BROWSERLESS_API_KEY")

# Configurar ADMINS e SERVER_EMAIL para envio de erros críticos
ADMINS = [("Prefeitura Municipal de Novo Horizonte",
           "suporte@novohorizonte.sp.gov.br")]
SERVER_EMAIL = "suporte@novohorizonte.sp.gov.br"
