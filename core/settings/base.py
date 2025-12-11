
"""
Configurações base para todos os ambientes.
"""
import os
from pathlib import Path

from django.contrib.messages import constants

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Separando as apps para melhor organização
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_extensions",
    "django_filters",
]

MY_APPS = [
    "dashboard.apps.DashboardConfig",
    "authenticate.apps.AuthenticateConfig",
    "bidding_supplier.apps.BiddingSupplierConfig",
    "reports.apps.ReportsConfig",
    "organizational_structure.apps.OrganizationalStructureConfig",
    "bidding_procurement.apps.BiddingProcurementConfig",
    "audit.apps.AuditConfig",  # Sistema de auditoria
    "core",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + MY_APPS


# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "authenticate.middleware.OnboardingMiddleware",  # Força onboarding em first_login
    "audit.middleware.AuditMiddleware",  # Auditoria de operações
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

AUTH_USER_MODEL = 'authenticate.ProfessionalUser'
LOGIN_URL = 'authenticate:login'
LOGOUT_URL = 'authenticate:logout'
LOGIN_REDIRECT_URL = 'dashboard:index'

# Configurações de Sessão (Auto-logout)
SESSION_COOKIE_AGE = 1800  # 30 minutos de inatividade
SESSION_SAVE_EVERY_REQUEST = True  # Renova sessão a cada requisição
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Logout ao fechar navegador


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles" / "static"

MEDIA_URL = 'media/images/'
MEDIA_ROOT = BASE_DIR / 'media' / 'images'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DEFAULT_FROM_EMAIL = "ti@novohorizonte.sp.gov.br"

# Configuração padrão de logging para todos os ambientes

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "django.log"))
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "simple": {
            "format": "%(levelname)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    },
}


# Mensagens do Django
MESSAGE_TAGS = {
    constants.ERROR: "flex items-center p-4 mb-4 text-sm text-red-800 border border-red-300 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400 dark:border-red-800 gap-4 w-full",
    constants.SUCCESS: "flex items-center p-4 mb-4 text-sm text-green-800 border border-green-300 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400 dark:border-green-800 gap-4 w-full",
    constants.WARNING: "flex items-center p-4 mb-4 text-sm text-yellow-800 border border-yellow-300 rounded-lg bg-yellow-50 dark:bg-gray-800 dark:text-yellow-300 dark:border-yellow-800 gap-4 w-full",
    constants.INFO: "flex items-center p-4 mb-4 text-sm text-blue-800 border border-blue-300 rounded-lg bg-blue-50 dark:bg-gray-800 dark:text-blue-400 dark:border-blue-800 gap-4 w-full",
}
