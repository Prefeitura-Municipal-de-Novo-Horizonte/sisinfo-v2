from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from authenticate.models import ProfessionalUser


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = ProfessionalUser
        fields = ["first_name", "last_name", "username",
                  "email", "registration", "profile_pic", "is_tech", "is_admin"]

    def clean_password2(self):
        # Check that the two password entries match
        import re
        pattern = re.compile("(?=(.*[a-z]){2,})(?=(.*[A-Z]){2,})")
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Senhas não combinam")
        elif len(password1) < 8:
            raise ValidationError("Senha deve conter no minímo 8 caracteres")
        elif pattern.match(password1):
            raise ValidationError(
                "Senha deve conter letras maiúsculas, minúsculas, números e caracteres especiais, como !, @, #, $, etc")
        return password2

    def clean_firstname(self):
        return self.extract_from_clean(self.first_name)

    def clean_lastname(self):
        return self.extract_from_clean(self.last_name)

    def clean_username(self):
        return self.extract_from_clean2(self.username)

    def extrac_from_clean2(self, field):
        username = self.cleaned_data[field]
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
