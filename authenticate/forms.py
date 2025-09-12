from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    ReadOnlyPasswordHashField,
)
from django.core.exceptions import ValidationError

from authenticate.models import ProfessionalUser


class FormStyleMixin:
    def apply_style_to_fields(self, style_type='default'):
        for field_name, field in self.fields.items():
            if style_type == 'user_creation' and field_name in ['is_tech', 'is_admin']:
                field.widget.attrs['class'] = "sr-only peer"
                continue

            if style_type == 'login':
                field.widget.attrs['class'] = "block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
            else:  # default style
                field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"


class UserCreationForm(FormStyleMixin, forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = ProfessionalUser
        fields = ["first_name", "last_name", "username",
                  "email", "registration", "is_tech", "is_admin"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style_to_fields(style_type='user_creation')

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

    def clean_username(self):
        username = self.cleaned_data['username']
        return username.lower()

    def extract_from_clean(self, field):
        name = self.cleaned_data[field]
        words = [w.capitalize() for w in name.split()]
        return ' '.join(words)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(FormStyleMixin, forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = ProfessionalUser
        fields = ["first_name", "last_name", "username",
                  "email", "registration"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style_to_fields()
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields["username"].widget.attrs["readonly"] = True


class AuthenticationFormCustom(FormStyleMixin, AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': ''}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': ''}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style_to_fields(style_type='login')


class PasswordChangeCustomForm(FormStyleMixin, PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_style_to_fields()
