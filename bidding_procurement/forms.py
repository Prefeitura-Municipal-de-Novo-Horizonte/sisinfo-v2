from django import forms

from core.mixins import CapitalizeFieldMixin
from core.constants import STANDARD_INPUT_CLASS
from bidding_procurement.models import Bidding, Material, MaterialBidding


class BiddingForm(CapitalizeFieldMixin, forms.ModelForm):
    class Meta:
        model = Bidding
        fields = [
            "name",
            "administrative_process",
            "date",
            "validity_date",
            "status"
        ]
        labels = {
            'name': 'Nome',
            'administrative_process': 'Processo Administrativo',
            'date': 'Data',
            'validity_date': 'Prazo de Validade',
            'status': 'Status',
        }
        help_texts = {
            'administrative_process': 'Ex: 121/25',
            'validity_date': 'Data de validade da licitação',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'validity_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = STANDARD_INPUT_CLASS

    def clean_name(self):
        return self.extract_from_clean("name")


class MaterialForm(CapitalizeFieldMixin, forms.ModelForm):
    class Meta:
        model = Material
        fields = ["name", "brand", "unit"]
        labels = {
            'name': 'Nome',
            'brand': 'Marca',
            'unit': 'Unidade',
        }
        help_texts = {
            'brand': 'Marca do material (ex: TSA AD-09, DEKO 764-J CAT6)',
            'unit': 'Unidade de medida (ex: un, M, pc, cx)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = STANDARD_INPUT_CLASS

    def clean_name(self):
        return self.extract_from_clean("name")


class MaterialBiddingForm(forms.ModelForm):
    class Meta:
        model = MaterialBidding
        fields = ["material", "quantity", "supplier", "price", "readjustment", "status"]
        labels = {
            'material': 'Material',
            'quantity': 'Quantidade',
            'supplier': 'Fornecedor',
            'price': 'Preço',
            'readjustment': 'Reajuste (%)',
            'status': 'Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = STANDARD_INPUT_CLASS
