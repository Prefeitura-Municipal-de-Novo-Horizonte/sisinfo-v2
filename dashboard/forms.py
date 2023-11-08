from django import forms
from django.core.exceptions import ValidationError

from dashboard.models import Direction


class DirectionForm(forms.ModelForm):
    class Meta:
        model = Direction
        fields = ['name', 'slug', 'accountable', 'kind']

    def clean_name(self):
        return self.extract_from_clean('name')
    
    def clean_accountable(self):
        return self.extract_from_clean('accountable')

    def extract_from_clean(self, field):
        name = self.cleaned_data[field]
        words = [w.capitalize() for w in name.split()]
        return ' '.join(words)