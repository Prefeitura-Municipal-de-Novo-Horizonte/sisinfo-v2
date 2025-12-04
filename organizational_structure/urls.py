from django.urls import path

from organizational_structure.views import (
    direction_create,
    direction_delete,
    direction_detail,
    direction_update,
    directions,
    sector_create,
    sector_delete,
    sector_detail,
    sector_update,
    sectors,
)

app_name = "organizational_structure"

urlpatterns = [
    # Diretorias
    path("diretorias/", directions, name="diretorias"),
    path("diretoria/create/", direction_create, name="create_diretoria"),
    path("diretoria/<slug:slug>/", direction_detail, name="diretoria"),
    path("diretoria/<slug:slug>/update/", direction_update, name="update_diretoria"),
    path(
        "diretoria/<slug:slug>/delete/",
        direction_delete,
        name="delete_diretoria",
    ),
    # Setores
    path("setores/", sectors, name="setores"),
    path("setor/create/", sector_create, name="create_setor"),
    path("diretoria/setor/<slug:slug>/", sector_detail, name="setor"),
    path("diretoria/setor/<slug:slug>/update/", sector_update, name="update_setor"),
    path("diretoria/setor/<slug:slug>/delete/", sector_delete, name="delete_setor"),
]
