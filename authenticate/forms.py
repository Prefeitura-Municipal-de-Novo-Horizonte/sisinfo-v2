from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    ReadOnlyPasswordHashField,
)
from django.core.exceptions import ValidationError

from core.mixins import CapitalizeFieldMixin
from core.constants import STANDARD_INPUT_CLASS
from authenticate.models import ProfessionalUser




class UserCreationForm(CapitalizeFieldMixin, forms.ModelForm):
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Confirmação de Senha", widget=forms.PasswordInput
    )

    class Meta:
        model = ProfessionalUser
        fields = ["first_name", "last_name",
                  "email", "registration", "is_tech", "is_admin"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['is_tech', 'is_admin']:
                # Checkboxes mantêm estilo padrão
                continue
            field.widget.attrs['class'] = STANDARD_INPUT_CLASS

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Senhas não combinam")
        return password2

    def clean_first_name(self):
        return self.extract_from_clean('first_name')

    def clean_last_name(self):
        return self.extract_from_clean('last_name')



    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user




class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = ProfessionalUser
        fields = ["first_name", "last_name",
                  "email", "registration"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS


class AuthenticationFormCustom(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': ''}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': ''}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Login mantém estilo floating label para consistência com página externa
        for field in self.fields.values():
            field.widget.attrs['class'] = "block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"


class PasswordChangeCustomForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = STANDARD_INPUT_CLASS
