from django.urls import path

from dashboard.views import directions, index, sectors

app_name = 'dashboard'

urlpatterns = [
    path('', index, name='index'),
    # Diretorias
    path('diretorias/', directions, name='diretorias'),
    # Setores
    path('setores/', sectors, name='setores'),
]
