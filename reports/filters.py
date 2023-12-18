import django_filters
from django.forms import DateInput, Select, TextInput
from django_filters import CharFilter, DateFilter

from reports.models import Report


class ReportFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='created_at',
                            lookup_expr='gte', widget=DateInput(format=('%Y/%m/%d'), attrs={'type': 'text', 'datepicker': '', 'datepicker-buttons': '','datepicker-format': 'yyyy-mm-dd','class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'placeholder': 'A partir de:'}))
    end_date = DateFilter(field_name='created_at', lookup_expr='lte', widget=DateInput(format=('%Y/%m/%d'), attrs={'type': 'text', 'datepicker': '', 'datepicker-buttons': '','datepicker-format': 'yyyy-mm-dd','class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500', 'placeholder': 'Até'}))
    justification = CharFilter(field_name='justification', lookup_expr='icontains', label="Pesquise por justificativa:", widget=TextInput(
        attrs={"class": "block pt-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 w-full max-w-full", "placeholder": "Justificativa"}))
    number_report = CharFilter(
        field_name='number_report', lookup_expr='icontains', label="Pesquise por numero do laudo:", widget=TextInput(
            attrs={"class": "block pt-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 w-full max-w-full", "placeholder": "Número do laudo"}))

    class Meta:
        model = Report
        fields = '__all__'
        exclude = ['created_at']
