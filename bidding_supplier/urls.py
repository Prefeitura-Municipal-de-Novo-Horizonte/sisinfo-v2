from django.urls import path

from bidding_supplier.views import supplier_detail, suppliers

app_name = 'suppliers'

urlpatterns = [
    path('', suppliers, name='fornecedores'),
    path("fornecedor/<slug:slug>/", supplier_detail, name="fornecedor"),
]
