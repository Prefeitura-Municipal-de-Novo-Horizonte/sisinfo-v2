from django.urls import path

from dashboard.views import (
    direction_delete,
    direction_detail,
    direction_edit,
    directions,
    index,
    sector_delete,
    sectors,
)

app_name = 'dashboard'

urlpatterns = [
    path('', index, name='index'),
    # Diretorias
    path('diretorias/', directions, name='diretorias'),
    path('diretoria/<slug:slug>/', direction_detail, name="diretoria"),
    #path('diretoria/edit/<slug:slug>/<id:id>', direction_edit, name="edit_diretoria"),
    path('diretoria/del/<str:id>/', direction_delete, name="delete_diretoria"),
    # Setores
    path('setores/', sectors, name='setores'),
    path('setor/del/<slug:slug>/<str:id>/', sector_delete, name='delete_setor'),
]
