from django import forms

from core.constants import STANDARD_INPUT_CLASS, TEXTAREA_CLASS
from core.mixins import CapitalizeFieldMixin, TailwindFormMixin
from organizational_structure.models import Direction, Sector


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
