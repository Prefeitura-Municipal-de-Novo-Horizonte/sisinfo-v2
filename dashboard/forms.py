from django import forms

from dashboard.models import Bidding, Direction, Material, Sector


##############################################################################################
############################ SETORES E DIRETORIAS ############################################
##############################################################################################
class DirectionForm(forms.ModelForm):
    class Meta:
        model = Direction
        fields = ["name", "accountable", "kind"]

    def clean_name(self):
        return self.extract_from_clean("name")

    def clean_accountable(self):
        return self.extract_from_clean("accountable")

    def extract_from_clean(self, field):
        name = self.cleaned_data[field]
        words = [w.capitalize() for w in name.split()]
        return " ".join(words)


class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ["name", "accountable", "direction", "phone", "email", "address"]

    def clean_name(self):
        return self.extract_from_clean("name")

    def clean_accountable(self):
        return self.extract_from_clean("accountable")

    def extract_from_clean(self, field):
        name = self.cleaned_data[field]
        words = [w.capitalize() for w in name.split()]
        return " ".join(words)

    def clean(self):
        self.cleaned_data = super().clean()
        if not self.cleaned_data.get("email") and not self.cleaned_data.get("phone"):
            raise forms.ValidationError("Informe ao menos um e-mail ou telefone.")
        return self.cleaned_data


##############################################################################################
########################### LICITAÇÃO E SUPRIMENTOS ##########################################
##############################################################################################


class BiddingForm(forms.ModelForm):
    class Meta:
        model = Bidding
        fields = ["name", "status", "date"]

    def clean_name(self):
        return self.extract_from_clean("name")

    def extract_from_clean(self, field):
        name = self.cleaned_data[field]
        words = [w.capitalize() for w in name.split()]
        return " ".join(words)


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ["name", "status", "bidding", "price", "readjustment"]

        def clean_name(self):
            return self.extract_from_clean("name")
