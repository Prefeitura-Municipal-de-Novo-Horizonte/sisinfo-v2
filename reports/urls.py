from django.urls import path

from reports.views import report_register, reports

app_name = 'reports'

urlpatterns = [
    path('', reports, name='reports'),
    path('new_register_report/', report_register, name='register_report'),
]
