from django.urls import path

from organizational_structure.views import (
    DirectionListView,
    DirectionCreateView,
    DirectionDetailView,
    DirectionUpdateView,
    DirectionDeleteView,
    SectorListView,
    SectorCreateView,
    SectorDetailView,
    SectorUpdateView,
    SectorDeleteView,
)

app_name = "organizational_structure"

urlpatterns = [
    # Diretorias
    path("diretorias/", DirectionListView.as_view(), name="diretorias"),
    path("diretoria/create/", DirectionCreateView.as_view(), name="create_diretoria"),
    path("diretoria/<slug:slug>/", DirectionDetailView.as_view(), name="diretoria"),
    path("diretoria/<slug:slug>/update/", DirectionUpdateView.as_view(), name="update_diretoria"),
    path("diretoria/<slug:slug>/delete/", DirectionDeleteView.as_view(), name="delete_diretoria"),
    # Setores
    path("setores/", SectorListView.as_view(), name="setores"),
    path("setor/create/", SectorCreateView.as_view(), name="create_setor"),
    path("diretoria/setor/<slug:slug>/", SectorDetailView.as_view(), name="setor"),
    path("diretoria/setor/<slug:slug>/update/", SectorUpdateView.as_view(), name="update_setor"),
    path("diretoria/setor/<slug:slug>/delete/", SectorDeleteView.as_view(), name="delete_setor"),
]
