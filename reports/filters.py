import django_filters
from django.forms import DateInput, Select, TextInput
from django_filters import CharFilter, DateFilter

from core.mixins import TailwindFilterMixin
from reports.models import Report


class ReportFilter(TailwindFilterMixin, django_filters.FilterSet):
    start_date = DateFilter(field_name='created_at',
                            lookup_expr='gte', widget=DateInput(format=('%Y/%m/%d'), attrs={'type': 'text', 'datepicker': '', 'datepicker-buttons': '','datepicker-format': 'yyyy-mm-dd', 'placeholder': 'A partir de:'}))
    end_date = DateFilter(field_name='created_at', lookup_expr='lte', widget=DateInput(format=('%Y/%m/%d'), attrs={'type': 'text', 'datepicker': '', 'datepicker-buttons': '','datepicker-format': 'yyyy-mm-dd', 'placeholder': 'Até'}))
    justification = CharFilter(field_name='justification', lookup_expr='icontains', label="Pesquise por justificativa:", widget=TextInput(
        attrs={"placeholder": "Justificativa"}))
    number_report = CharFilter(
        field_name='number_report', lookup_expr='icontains', label="Pesquise por numero do laudo:", widget=TextInput(
            attrs={"placeholder": "Número do laudo"}))

    class Meta:
        model = Report
        fields = '__all__'
        exclude = ['created_at']
