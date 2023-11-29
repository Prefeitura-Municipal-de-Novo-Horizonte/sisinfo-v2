from django.urls import path

from bidding_supplier.views import suppliers

app_name = 'suppliers'

urlpatterns = [
    path('', suppliers, name='fornecedores'),
]
