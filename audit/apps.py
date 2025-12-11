"""
Configuração do app de auditoria.
"""
from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit'
    verbose_name = 'Sistema de Auditoria'

    def ready(self):
        """Importa signals quando o app estiver pronto"""
        import audit.signals  # noqa
