from django.urls import path

from dashboard.views import direction_detail, directions, index, sectors

app_name = 'dashboard'

urlpatterns = [
    path('', index, name='index'),
    # Diretorias
    path('diretorias/', directions, name='diretorias'),
    path('diretoria/<slug:slug>', direction_detail, name="diretoria"),
    # Setores
    path('setores/', sectors, name='setores'),
]
