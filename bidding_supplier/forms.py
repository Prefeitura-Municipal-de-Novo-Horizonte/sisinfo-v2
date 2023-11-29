from django import forms
from pycpfcnpj import cpfcnpj

from django.forms import inlineformset_factory

from bidding_supplier.models import Contact, Supplier


class SupplierForm(forms.Form):
    class Meta:
        models = Supplier
        fields = ['company', 'trade', 'cnpj', 'address']

    def clean_company(self):
        return self.extract_from_clean_company("company")

    def extract_from_clean(self, field):
        name = self.cleaned_data[field]
        words = [w.capitalize() for w in name.split()]
        return " ".join(words)

    def clean(self):
        self.cleaned_data = super().clean()
        if cpfcnpj.validate(self.cleaned_data.get("cnpj")) is False:
            raise forms.ValidationError("CNPJ Inválido!")
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field not in [self.fields["address"]]:
                field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
            else:
                field.widget.attrs['class'] = "block p-2.5 px-0 mt-1 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                field.widget.attrs['rows'] = "4"


class ContactForm(forms.Form):
    class Meta:
        model = Contact
        fields = ["kind", "value", "whatsapp"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field not in [self.fields["whatsapp"]]:
                field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
            else:
                field.widget.attrs['class'] = "sr-only peer"

ContactInlineForm = inlineformset_factory(
    Supplier,
    Contact,
    form=ContactForm,
    extra=0,
    can_delete=False,
    min_num=1,
    validate_min=True,
    )