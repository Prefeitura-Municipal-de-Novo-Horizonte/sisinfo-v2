from django.urls import path

from reports.views import report_register, report_view, reports

app_name = 'reports'

urlpatterns = [
    path('', reports, name='reports'),
    path('new_register_report/', report_register, name='register_report'),
    path('report/<slug:slug>', report_view, name='report_view'),
]
