"""
Configuração do Sentry para error tracking.
Usado em produção e opcionalmente em desenvolvimento.

Para criar uma conta gratuita:
https://sentry.io/signup/ (5.000 erros/mês)
"""
import sentry_sdk
from decouple import config

SENTRY_DSN = config("SENTRY_DSN", default="")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Sample rate para performance (10% das transações)
        traces_sample_rate=0.1,
        # Sample rate para profiling (10%)
        profiles_sample_rate=0.1,
        # Detecta ambiente automaticamente (development/production)
        environment=config("DJANGO_SETTINGS_MODULE", "").split(".")[-1],
        # Não enviar dados pessoais (LGPD)
        send_default_pii=False,
        # Capturar erros de console
        attach_stacktrace=True,
    )
