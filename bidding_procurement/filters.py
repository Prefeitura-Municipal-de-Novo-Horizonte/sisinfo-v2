import django_filters
from django_filters import CharFilter

from core.mixins import TailwindFilterMixin
from bidding_procurement.models import Bidding, Material


class MaterialFilter(TailwindFilterMixin, django_filters.FilterSet):
    name = CharFilter(label="Pesquise pelo nome do material:", field_name="name", lookup_expr="icontains")


class BiddingFilter(TailwindFilterMixin, django_filters.FilterSet):
    name = CharFilter(label="Pesquise pelo nome do processo:", field_name="name", lookup_expr="icontains")
