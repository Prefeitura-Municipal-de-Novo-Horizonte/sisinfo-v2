from django import forms

from core.mixins import CapitalizeFieldMixin
from bidding_procurement.models import Bidding, Material, MaterialBidding

# Constante de Estilo (Padronização com reports e organizational_structure)
STANDARD_INPUT_CLASS = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-500 focus:border-brand-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-brand-500 dark:focus:border-brand-500"


class BiddingForm(CapitalizeFieldMixin, forms.ModelForm):
    class Meta:
        model = Bidding
        fields = ["name", "date", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = STANDARD_INPUT_CLASS

    def clean_name(self):
        return self.extract_from_clean("name")


class MaterialForm(CapitalizeFieldMixin, forms.ModelForm):
    class Meta:
        model = Material
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = STANDARD_INPUT_CLASS

    def clean_name(self):
        return self.extract_from_clean("name")


class MaterialBiddingForm(forms.ModelForm):
    class Meta:
        model = MaterialBidding
        fields = ["material", "supplier", "price", "readjustment", "status"]
        labels = {
            'material': 'Material',
            'supplier': 'Fornecedor',
            'price': 'Preço',
            'readjustment': 'Reajuste (%)',
            'status': 'Status',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = STANDARD_INPUT_CLASS
