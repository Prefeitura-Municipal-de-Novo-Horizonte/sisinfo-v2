import django_filters
from django.forms import TextInput
from django_filters import CharFilter

from dashboard.models import Direction, Sector


##############################################################################################
############################ SETORES E DIRETORIAS ############################################
##############################################################################################
class DirectionFilter(django_filters.FilterSet):
    name = CharFilter(label="Pesquise por nome:", field_name="name", lookup_expr="icontains", widget=TextInput(attrs={
        "class": "block pt-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 w-full max-w-full"}))
    accountable = CharFilter(label="Pesquise pelo responsável:", field_name="accountable", lookup_expr="icontains", widget=TextInput(attrs={
        "class": "block pt-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 w-full max-w-full"}))

    class Meta:
        model = Direction
        fields = "__all__"


class SectorFilter(django_filters.FilterSet):
    name = CharFilter(label="Pesquise por nome:", field_name="name", lookup_expr="icontains", widget=TextInput(attrs={
        "class": "block pt-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 w-full max-w-full"}))
    accountable = CharFilter(label="Pesquise pelo responsável:",                                                                                                field_name="accountable", lookup_expr="icontains", widget=TextInput(attrs={
        "class": "block pt-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 w-full max-w-full"}))

    class Meta:
        model = Sector
        fields = ["name", "accountable"]


##############################################################################################
########################### LICITAÇÃO E SUPRIMENTOS ##########################################
##############################################################################################


class MaterialFilter(django_filters.FilterSet):
    name = CharFilter(label="Pesquise pelo nome do material:", field_name="name", lookup_expr="icontains", widget=TextInput(attrs={
        "class": "block pt-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 w-full max-w-full"}))


class BiddingFilter(django_filters.FilterSet):
    name = CharFilter(label="Pesquise pelo nome do processo:", field_name="name", lookup_expr="icontains", widget=TextInput(attrs={
        "class": "block pt-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 w-full max-w-full"}))
