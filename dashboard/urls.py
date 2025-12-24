from django.urls import path

from dashboard.views import (
    index, reports_by_sector_chart, top_materials_chart, api_status, 
    clean_ocr_jobs, backup_database, backup_start, backup_process, 
    backup_status, backup_download, admin_panel,
    bulk_close_reports, bulk_complete_deliveries
)

app_name = "dashboard"

urlpatterns = [
    path("", index, name="index"),
    path("manutencao/", admin_panel, name="admin_panel"),
    path("chart/reports-sector/", reports_by_sector_chart, name="reports_by_sector_chart"),
    path("chart/top-materials/", top_materials_chart, name="top_materials_chart"),
    path("api-status/", api_status, name="api_status"),
    path("manutencao/clean-ocr-jobs/", clean_ocr_jobs, name="clean_ocr_jobs"),
    # Backup síncrono (fallback)
    path("manutencao/backup/", backup_database, name="backup_database"),
    # Backup assíncrono
    path("manutencao/backup/start/", backup_start, name="backup_start"),
    path("manutencao/backup/process/<uuid:job_id>/", backup_process, name="backup_process"),
    path("manutencao/backup/status/<uuid:job_id>/", backup_status, name="backup_status"),
    path("manutencao/backup/download/<uuid:job_id>/", backup_download, name="backup_download"),
    # Bulk actions
    path("manutencao/bulk-close-reports/", bulk_close_reports, name="bulk_close_reports"),
    path("manutencao/bulk-complete-deliveries/", bulk_complete_deliveries, name="bulk_complete_deliveries"),
]
