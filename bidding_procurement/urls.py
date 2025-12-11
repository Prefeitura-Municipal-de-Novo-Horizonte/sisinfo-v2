from django.urls import path

from bidding_procurement.views import (
    # Bidding Views
    BiddingListView,
    BiddingCreateView,
    BiddingDetailView,
    BiddingUpdateView,
    BiddingDeleteView,
    BiddingToggleStatusView,
    # Material Views
    MaterialListView,
    MaterialCreateView,
    MaterialDetailView,
    MaterialUpdateView,
    MaterialDeleteView,
    MaterialToggleStatusView,
)

app_name = "bidding_procurement"

urlpatterns = [
    # Licitação - URLs combinadas para list/create
    path("licitacoes/", BiddingListView.as_view(), name="licitacoes"),
    path("licitacoes/criar/", BiddingCreateView.as_view(), name="criar_licitacao"),
    path("licitacao/<slug:slug>/", BiddingDetailView.as_view(), name="licitacao"),
    path("licitacao/<slug:slug>/update/", BiddingUpdateView.as_view(), name="update_licitacao"),
    path("licitacao/<slug:slug>/toggle-status/", BiddingToggleStatusView.as_view(), name="toggle_status_licitacao"),
    path("licitacao/<slug:slug>/delete/", BiddingDeleteView.as_view(), name="delete_licitacao"),
    
    # Materiais - URLs combinadas para list/create
    path("materiais/", MaterialListView.as_view(), name="materiais"),
    path("materiais/criar/", MaterialCreateView.as_view(), name="criar_material"),
    path("material/<slug:slug>/", MaterialDetailView.as_view(), name="material"),
    path("material/<slug:slug>/update/", MaterialUpdateView.as_view(), name="update_material"),
    path("material/<int:id>/toggle-status/", MaterialToggleStatusView.as_view(), name="toggle_status_material"),
    path("material/<slug:slug>/delete/", MaterialDeleteView.as_view(), name="delete_material"),
]
