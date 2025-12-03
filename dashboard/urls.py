from django.urls import path

from dashboard.views import index, reports_by_sector_chart

app_name = "dashboard"

urlpatterns = [
    path("", index, name="index"),
    path("chart/reports-sector/", reports_by_sector_chart, name="reports_by_sector_chart"),
]
