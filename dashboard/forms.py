from django import forms

from dashboard.models import Direction, Sector


class DirectionForm(forms.ModelForm):
    class Meta:
        model = Direction
        fields = ['name', 'accountable', 'kind']

    def clean_name(self):
        return self.extract_from_clean('name')
    
    def clean_accountable(self):
        return self.extract_from_clean('accountable')

    def extract_from_clean(self, field):
        name = self.cleaned_data[field]
        words = [w.capitalize() for w in name.split()]
        return ' '.join(words)

class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['name', 'accountable', 'direction', 'phone', 'email', 'address']

    def clean_name(self):
        return self.extract_from_clean('name')
    
    def clean_accountable(self):
        return self.extract_from_clean('accountable')

    def extract_from_clean(self, field):
        name = self.cleaned_data[field]
        words = [w.capitalize() for w in name.split()]
        return ' '.join(words)
    
    def clean(self):
        self.cleaned_data = super().clean()
        if not self.cleaned_data.get('email') and not self.cleaned_data.get('phone'):
            raise forms.ValidationError("Informe ao menos um e-mail ou telefone.")
        return self.cleaned_data
    