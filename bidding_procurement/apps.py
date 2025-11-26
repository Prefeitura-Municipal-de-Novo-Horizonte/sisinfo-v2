from django.apps import AppConfig


class BiddingProcurementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bidding_procurement"

    def ready(self):
        import bidding_procurement.signals
