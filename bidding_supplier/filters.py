"""
Filtros para busca de fornecedores.
"""
import django_filters
from django_filters import CharFilter

from core.mixins import TailwindFilterMixin
from bidding_supplier.models import Supplier


class SupplierFilter(TailwindFilterMixin, django_filters.FilterSet):
    """
    Filtro para fornecedores com busca por nome fantasia, razão social e CNPJ.
    """
    trade = CharFilter(
        label="Nome Fantasia:",
        field_name="trade",
        lookup_expr="icontains"
    )
    company = CharFilter(
        label="Razão Social:",
        field_name="company",
        lookup_expr="icontains"
    )
    cnpj = CharFilter(
        label="CNPJ:",
        field_name="cnpj",
        lookup_expr="icontains"
    )
    
    class Meta:
        model = Supplier
        fields = ['trade', 'company', 'cnpj']
