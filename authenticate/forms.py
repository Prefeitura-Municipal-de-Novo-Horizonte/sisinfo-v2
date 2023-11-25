from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from django.core.exceptions import ValidationError

from authenticate.models import ProfessionalUser


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = ProfessionalUser
        fields = ["first_name", "last_name", "username",
                  "email", "registration", "is_tech", "is_admin"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Senhas não combinam")
        return password2

    def clean_firstname(self):
        return self.extract_from_clean(self.first_name)

    def clean_lastname(self):
        return self.extract_from_clean(self.last_name)

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


class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = ProfessionalUser
        fields = ["first_name", "last_name", "username",
                  "email", "registration"]

    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields["username"].widget.attrs["readonly"] = True


class AuthenticationFormCustom(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Digite seu usenarme ...'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua senha ...'}))

    class Meta:
        model = ProfessionalUser
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = "bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"