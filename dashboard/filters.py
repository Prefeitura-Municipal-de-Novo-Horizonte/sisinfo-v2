import django_filters
from django_filters import CharFilter

from dashboard.models import Direction, Sector


################################################################
################## DIRETORIA E SETORES #########################
################################################################
class DirectionFilter(django_filters.FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")
    accountable = CharFilter(field_name="accountable", lookup_expr="icontains")

    class Meta:
        model = Direction
        fields = '__all__'


class SectorFilter(django_filters.FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")
    accountable = CharFilter(field_name="accountable", lookup_expr="icontains")

    class Meta:
        model = Sector
        fields = ['name', 'accountable']
    