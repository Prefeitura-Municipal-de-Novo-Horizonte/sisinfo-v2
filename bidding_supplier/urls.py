from django.urls import path

from bidding_supplier.views import supplier_detail, supplier_update, suppliers

app_name = 'suppliers'

urlpatterns = [
    path('', suppliers, name='fornecedores'),
    path("fornecedor/<slug:slug>/", supplier_detail, name="fornecedor"),
    path('fornecedor/<slug:slug>/update',
         supplier_update, name="fornecedor_update"),
]
