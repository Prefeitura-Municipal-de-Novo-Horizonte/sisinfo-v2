from django.urls import path

from dashboard.views import (
    index,

)

app_name = "dashboard"

urlpatterns = [
    path("", index, name="index"),


]
