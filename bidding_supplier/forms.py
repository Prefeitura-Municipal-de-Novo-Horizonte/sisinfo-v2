from django import forms
from django.forms import inlineformset_factory
from pycpfcnpj import cpfcnpj

from core.mixins import CapitalizeFieldMixin, TailwindFormMixin
from bidding_supplier.models import Contact, Supplier


class SupplierForm(TailwindFormMixin, CapitalizeFieldMixin, forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['company', 'trade', 'cnpj', 'address']

    def clean_company(self):
        return self.extract_from_clean("company")

    def clean(self):
        self.cleaned_data = super().clean()
        if cpfcnpj.validate(self.cleaned_data.get("cnpj")) is False:
            raise forms.ValidationError("CNPJ Inválido!")
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override address field style
        self.fields['address'].widget.attrs['class'] = "block p-2.5 px-0 mt-1 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        self.fields['address'].widget.attrs['rows'] = "4"


class ContactForm(TailwindFormMixin, forms.ModelForm):
    id = forms.IntegerField()

    class Meta:
        model = Contact
        fields = ['id', 'kind', 'value', 'whatsapp']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override whatsapp field style
        self.fields['whatsapp'].widget.attrs['class'] = "sr-only peer"

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
