import django_filters
from django_filters import CharFilter, DateFilter, ChoiceFilter

from core.mixins import TailwindFilterMixin
from bidding_procurement.models import Bidding, Material, STATUS_CHOICES


class MaterialFilter(TailwindFilterMixin, django_filters.FilterSet):
    """Filtro para materiais com busca por nome, marca e unidade."""
    name = CharFilter(
        label="Pesquise pelo nome do material:",
        field_name="name",
        lookup_expr="icontains"
    )
    brand = CharFilter(
        label="Marca:",
        field_name="brand",
        lookup_expr="icontains"
    )
    unit = CharFilter(
        label="Unidade:",
        field_name="unit",
        lookup_expr="icontains"
    )
    
    class Meta:
        model = Material
        fields = ['name', 'brand', 'unit']


class BiddingFilter(TailwindFilterMixin, django_filters.FilterSet):
    """Filtro para licitações com busca por nome, data e status."""
    name = CharFilter(
        label="Pesquise pelo nome do processo:",
        field_name="name",
        lookup_expr="icontains"
    )
    date = DateFilter(
        label="Data:",
        field_name="date",
        lookup_expr="exact"
    )
    status = ChoiceFilter(
        label="Status:",
        field_name="status",
        choices=STATUS_CHOICES
    )
    
    class Meta:
        model = Bidding
        fields = ['name', 'date', 'status']
