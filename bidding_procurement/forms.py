from django import forms

from core.mixins import CapitalizeFieldMixin, TailwindFormMixin
from bidding_procurement.models import Bidding, Material, MaterialBidding


class BiddingForm(TailwindFormMixin, CapitalizeFieldMixin, forms.ModelForm):
    class Meta:
        model = Bidding
        fields = ["name", "date", "status"]

    def clean_name(self):
        return self.extract_from_clean("name")


class MaterialForm(TailwindFormMixin, CapitalizeFieldMixin, forms.ModelForm):
    class Meta:
        model = Material
        fields = ["name"]

    def clean_name(self):
        return self.extract_from_clean("name")


class MaterialBiddingForm(TailwindFormMixin, forms.ModelForm):
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
