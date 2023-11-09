from django.urls import path

from dashboard.views import (
    direction_delete,
    direction_detail,
    direction_update,
    directions,
    index,
    sector_delete,
    sector_detail,
    sector_update,
    sectors,
)

app_name = 'dashboard'

urlpatterns = [
    path('', index, name='index'),
    # Diretorias
    path('diretorias/', directions, name='diretorias'),
    path('diretoria/<slug:slug>/', direction_detail, name="diretoria"),
    path('diretoria/<slug:slug>/update/', direction_update, name="update_diretoria"),
    path('diretoria/<slug:slug>/<str:id>/delete/', direction_delete, name="delete_diretoria"),
    # Setores
    path('setores/', sectors, name='setores'),
    path('diretoria/setor/<slug:slug>/', sector_detail, name="setor"),
    path('diretoria/setor/<slug:slug>/update/', sector_update, name="update_setor"),
    path('diretoria/setor/<slug:slug>/<str:id>/delete/', sector_delete, name='delete_setor'),
]
