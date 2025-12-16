from django.urls import path

from bidding_supplier.views import (
    ContactDeleteView,
    SupplierCreateView,
    SupplierDeleteView,
    SupplierDetailView,
    SupplierListView,
    SupplierUpdateView,
)

app_name = 'suppliers'

urlpatterns = [
    # Listagem e criação
    path('', SupplierListView.as_view(), name='fornecedores'),
    path('criar/', SupplierCreateView.as_view(), name='fornecedor_create'),
    
    # Detalhes, edição e exclusão
    path("fornecedor/<slug:slug>/", SupplierDetailView.as_view(), name="fornecedor"),
    path('fornecedor/update/<slug:slug>/', SupplierUpdateView.as_view(), name="fornecedor_update"),
    path('fornecedor/delete/<slug:slug>/', SupplierDeleteView.as_view(), name="fornecedor_delete"),
    
    # Contatos
    path('fornecedor/contato/<str:id>/', ContactDeleteView.as_view(), name="contato_delete"),
]
