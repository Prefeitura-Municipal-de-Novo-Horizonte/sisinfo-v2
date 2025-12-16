from django.urls import path

    ReportDetailView,
    ReportListView,
    create_sector_api,
    generate_pdf_report,
    material_report_delete,
    report_register,
    report_update,
)

app_name = 'reports'

urlpatterns = [
    path('', ReportListView.as_view(), name='reports'),
    path('new_register_report/', report_register, name='register_report'),
    path('report/<slug:slug>', ReportDetailView.as_view(), name='report_view'),
    path('report/<slug:slug>/update', report_update, name='report_update'),
    path('report/<slug:report_slug>/material/<int:pk>/delete',
         material_report_delete, name="material_report_delete"),
    path('report/<slug:slug>/download-pdf', generate_pdf_report, name='generate_pdf'),
    path('api/create-sector/', create_sector_api, name='create_sector_api'),
]
