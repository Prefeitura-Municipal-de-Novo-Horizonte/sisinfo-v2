from django.urls import path

from bidding_supplier.views import (
    contact_supplier_delete,
    supplier_delete,
    supplier_detail,
    supplier_update,
    suppliers,
)

app_name = 'suppliers'

urlpatterns = [
    path('', suppliers, name='fornecedores'),
    path("fornecedor/<slug:slug>/", supplier_detail, name="fornecedor"),
    path('fornecedor/update/<slug:slug>/',
         supplier_update, name="fornecedor_update"),
    path('fornecedor/delete/<slug:slug>/',
         supplier_delete, name="fornecedor_delete"),
    # Contatos
    path('fornecedor/contato/<str:id>/',
         contact_supplier_delete, name="contato_delete"),
]
