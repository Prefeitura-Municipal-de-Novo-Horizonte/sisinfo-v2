from django import forms
from django.forms import inlineformset_factory
from pycpfcnpj import cpfcnpj

from core.mixins import CapitalizeFieldMixin
from bidding_supplier.models import Contact, Supplier

# Constante de Estilo (Padronização)
STANDARD_INPUT_CLASS = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-500 focus:border-brand-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-brand-500 dark:focus:border-brand-500"
TEXTAREA_CLASS = "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-brand-500 dark:focus:border-brand-500"


class SupplierForm(CapitalizeFieldMixin, forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['company', 'trade', 'cnpj', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'address':
                field.widget.attrs['class'] = TEXTAREA_CLASS
            else:
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS

    def clean_company(self):
        return self.extract_from_clean("company")

    def clean(self):
        self.cleaned_data = super().clean()
        if cpfcnpj.validate(self.cleaned_data.get("cnpj")) is False:
            raise forms.ValidationError("CNPJ Inválido!")
        return self.cleaned_data


class ContactForm(forms.ModelForm):
    id = forms.IntegerField()

    class Meta:
        model = Contact
        fields = ['id', 'kind', 'value', 'whatsapp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'whatsapp' and not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS
        
        self.fields['id'].label = ''
        self.fields['id'].widget = forms.HiddenInput()


ContactInlineForm = inlineformset_factory(
    Supplier,
    Contact,
    form=ContactForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
