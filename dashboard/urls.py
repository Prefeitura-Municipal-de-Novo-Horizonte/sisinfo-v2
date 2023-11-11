from django.urls import path

from dashboard.views import (
    bidding_delete,
    bidding_detail,
    bidding_update,
    biddings,
    direction_delete,
    direction_detail,
    direction_update,
    directions,
    index,
    material_delete,
    material_detail,
    material_update,
    materials,
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
    path('diretoria/<slug:slug>/update/',
         direction_update, name="update_diretoria"),
    path('diretoria/<slug:slug>/<str:id>/delete/',
         direction_delete, name="delete_diretoria"),
    # Setores
    path('setores/', sectors, name='setores'),
    path('diretoria/setor/<slug:slug>/', sector_detail, name="setor"),
    path('diretoria/setor/<slug:slug>/update/',
         sector_update, name="update_setor"),
    path('diretoria/setor/<slug:slug>/<str:id>/delete/',
         sector_delete, name='delete_setor'),
    # Licitação
    path('licitacoes/', biddings, name='licitacoes'),
    path('licitacao/<slug:slug>/', bidding_detail, name="licitacao"),
    path('licitacao/<slug:slug>/update/',
         bidding_update, name="update_licitacao"),
    path('licitacao/<slug:slug>/<str:id>/delete/',
         bidding_delete, name='delete_licitacao'),
    # Materiais
    path('materiais/', materials, name='materiais'),
    path('material/<slug:slug>/', material_detail, name='material'),
    path('material/<slug:slug>/update/',
         material_update, name="update_material"),
    path('material/<slug:slug>/<str:id>/delete/',
         material_delete, name='delete_material'),
]
