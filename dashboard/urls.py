from django.urls import path

from dashboard.views import index, reports_by_sector_chart, top_materials_chart, api_status

app_name = "dashboard"

urlpatterns = [
    path("", index, name="index"),
    path("chart/reports-sector/", reports_by_sector_chart, name="reports_by_sector_chart"),
    path("chart/top-materials/", top_materials_chart, name="top_materials_chart"),
    path("api-status/", api_status, name="api_status"),
]
