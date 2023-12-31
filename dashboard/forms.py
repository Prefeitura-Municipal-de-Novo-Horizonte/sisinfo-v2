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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"


class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ["name", "accountable",
                  "direction", "phone", "email", "address"]

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
            raise forms.ValidationError(
                "Informe ao menos um e-mail ou telefone.")
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field not in [self.fields["address"]]:
                field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
            else:
                field.widget.attrs['class'] = "block p-2.5 px-0 mt-1 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                field.widget.attrs['rows'] = "4"


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ["name", "status", "bidding",
                  "price", "readjustment", "supplier"]

        def clean_name(self):
            return self.extract_from_clean("name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
