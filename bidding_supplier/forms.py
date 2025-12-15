from django import forms
from django.forms import inlineformset_factory
from validate_docbr import CNPJ

from core.mixins import CapitalizeFieldMixin
from core.constants import STANDARD_INPUT_CLASS, TEXTAREA_CLASS
from bidding_supplier.models import Contact, Supplier


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
        cnpj = self.cleaned_data.get("cnpj")
        
        # Alerta se CNPJ estiver vazio
        if not cnpj or cnpj.strip() == "":
            raise forms.ValidationError("CNPJ precisa ser preenchido!")
        
        # Valida CNPJ se preenchido
        cnpj_validator = CNPJ()
        if not cnpj_validator.validate(cnpj):
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
