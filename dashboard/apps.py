from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard"

    def ready(self):
        """Importa signals de cache quando o app é carregado."""
        # Importa signals para invalidação automática de cache
        import core.signals  # noqa: F401
