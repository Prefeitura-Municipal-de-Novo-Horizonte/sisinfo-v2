from django.apps import AppConfig


class OrganizationalStructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organizational_structure"

    def ready(self):
        import organizational_structure.signals
