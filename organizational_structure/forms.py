from django import forms

from core.mixins import CapitalizeFieldMixin, TailwindFormMixin
from organizational_structure.models import Direction, Sector

# Constantes de Estilo (Padronização)
STANDARD_INPUT_CLASS = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
TEXTAREA_CLASS = "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"


class DirectionForm(TailwindFormMixin, CapitalizeFieldMixin, forms.ModelForm):
    class Meta:
        model = Direction
        fields = ["name", "accountable"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = STANDARD_INPUT_CLASS

    def clean_name(self):
        return self.extract_from_clean("name")

    def clean_accountable(self):
        return self.extract_from_clean("accountable")


class SectorForm(TailwindFormMixin, CapitalizeFieldMixin, forms.ModelForm):
    class Meta:
        model = Sector
        fields = ["name", "accountable",
                  "direction", "phone", "email", "address"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'address':
                field.widget.attrs['class'] = TEXTAREA_CLASS
            else:
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS

    def clean_name(self):
        return self.extract_from_clean("name")

    def clean_accountable(self):
        return self.extract_from_clean("accountable")

    def clean(self):
        self.cleaned_data = super().clean()
        if not self.cleaned_data.get("email") and not self.cleaned_data.get("phone"):
            raise forms.ValidationError(
                "Informe ao menos um e-mail ou telefone.")
        return self.cleaned_data
