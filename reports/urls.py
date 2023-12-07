from django.urls import path

from reports.views import material_report_delete, pdf_report, report_register, report_update, report_view, reports

app_name = 'reports'

urlpatterns = [
    path('', reports, name='reports'),
    path('new_register_report/', report_register, name='register_report'),
    path('report/<slug:slug>', report_view, name='report_view'),
    path('report/<slug:slug>/update', report_update, name='report_update'),
    path('report/material_report/<str:id>',
         material_report_delete, name='material_report_delete'),
    path('report/<slug:slug>/pdf', pdf_report, name='pdf_report'),
]
