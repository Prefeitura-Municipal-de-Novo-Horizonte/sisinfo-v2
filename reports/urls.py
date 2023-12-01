from django.urls import path
from reports.views import reports

urlpatterns = [
    path('', reports, name='reports')
]
