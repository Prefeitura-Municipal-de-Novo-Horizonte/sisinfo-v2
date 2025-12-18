from django.apps import AppConfig

class FiscalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fiscal'
    verbose_name = 'Gestão Fiscal'

    def ready(self):
        import fiscal.signals
