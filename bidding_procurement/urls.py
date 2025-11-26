from django.urls import path

from bidding_procurement.views import (
    bidding_delete,
    bidding_detail,
    bidding_update,
    biddings,
    material_delete,
    material_detail,
    material_update,
    materials,
    toggle_bidding_status,
    toggle_material_status,
)

app_name = "bidding_procurement"

urlpatterns = [
    # Licitação
    path("licitacoes/", biddings, name="licitacoes"),
    path("licitacao/<slug:slug>/", bidding_detail, name="licitacao"),
    path("licitacao/<slug:slug>/update/", bidding_update, name="update_licitacao"),
    path("licitacao/<slug:slug>/toggle-status/", toggle_bidding_status, name="toggle_status_licitacao"),
    path("licitacao/<slug:slug>/delete/", bidding_delete, name="delete_licitacao"),
    # Materiais
    path("materiais/", materials, name="materiais"),
    path("material/<slug:slug>/", material_detail, name="material"),
    path("material/<slug:slug>/update/", material_update, name="update_material"),
    path("material/<int:id>/toggle-status/", toggle_material_status, name="toggle_status_material"),
    path(
        "material/<slug:slug>/delete/", material_delete, name="delete_material"
    ),
]
