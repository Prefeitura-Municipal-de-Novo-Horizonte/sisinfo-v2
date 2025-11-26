from django.urls import path

from reports.views import (
    material_report_delete,
    pdf_report,
    report_register,
    report_update,
    report_view,
    reports,
    generate_pdf_report
)

app_name = 'reports'

urlpatterns = [
    path('', reports, name='reports'),
    path('new_register_report/', report_register, name='register_report'),
    path('report/<slug:slug>', report_view, name='report_view'),
    path('report/<slug:slug>/update', report_update, name='report_update'),
    path('report/<slug:report_slug>/material/<int:pk>/delete',
         material_report_delete, name="material_report_delete"),
    path('report/<slug:slug>/pdf', pdf_report, name='pdf_report'),
    path('report/<slug:slug>/download-pdf', generate_pdf_report, name='generate_pdf'),
]
