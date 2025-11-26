import django_filters
from django_filters import CharFilter

from core.mixins import TailwindFilterMixin
from organizational_structure.models import Direction, Sector


class DirectionFilter(TailwindFilterMixin, django_filters.FilterSet):
    name = CharFilter(label="Pesquise por nome:", field_name="name", lookup_expr="icontains")
    accountable = CharFilter(label="Pesquise pelo responsável:", field_name="accountable", lookup_expr="icontains")

    class Meta:
        model = Direction
        fields = "__all__"


class SectorFilter(TailwindFilterMixin, django_filters.FilterSet):
    name = CharFilter(label="Pesquise por nome:", field_name="name", lookup_expr="icontains")
    accountable = CharFilter(label="Pesquise pelo responsável:", field_name="accountable", lookup_expr="icontains")

    class Meta:
        model = Sector
        fields = ["name", "accountable"]
