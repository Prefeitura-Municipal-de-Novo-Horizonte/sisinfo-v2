from django import forms
from django.forms import inlineformset_factory

from authenticate.models import ProfessionalUser
from dashboard.models import Material
from reports.models import InterestRequestMaterial, Invoice, MaterialReport, Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['sector', 'employee', 'status',
                  'justification', 'professional', 'pro_accountable']

        def clean_employee(self):
            employee = self.cleaned_data["employee"]
            words = [w.capitalize() for w in employee.split()]
            return " ".join(words)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")  # store value of request
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field in [self.fields["justification"]]:
                field.widget.attrs['class'] = "block p-2.5 px-0 mt-1 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                field.widget.attrs['rows'] = "4"
            else:
                field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
                if field in [self.fields["professional"]]:
                    professional = ProfessionalUser.objects.filter(
                        id=self.request.user.id)
                    field.queryset = professional
                    field.widget.attrs['value'] = self.request.user.id
                    field.widget.attrs['selected'] = self.request.user.id
                    field.widget.attrs['data-placeholder'] = self.request.user
                    field.initial = self.request.user.id
                if field in [self.fields["pro_accountable"]]:
                    if self.request.user.is_tech is True and self.request.user.username != 'administrador':
                        professional = ProfessionalUser.objects.filter(
                            id=self.request.user.id)
                        field.queryset = professional
                        field.widget.attrs['value'] = self.request.user.id
                        field.widget.attrs['selected'] = self.request.user.id
                        field.widget.attrs['data-placeholder'] = self.request.user
                        field.initial = self.request.user.id
                    else:
                        professional = ProfessionalUser.objects.filter(
                            is_tech=True)
                        field.queryset = professional


class ReportUpdateForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['sector', 'employee', 'status',
                  'justification']

        def clean_employee(self):
            employee = self.cleaned_data["employee"]
            words = [w.capitalize() for w in employee.split()]
            return " ".join(words)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")  # store value of request
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field in [self.fields["justification"]]:
                field.widget.attrs['class'] = "block p-2.5 px-0 mt-1 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                field.widget.attrs['rows'] = "4"
            else:
                field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"


################################
## Materiais ###################
################################
class MaterialReportForm(forms.ModelForm):
    id = forms.IntegerField()

    class Meta:
        model = MaterialReport
        fields = ['id', 'material', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"

        self.fields['id'].label = ''
        self.fields['id'].widget = forms.HiddenInput()

        items_ativos = Material.objects.all()
        self.fields['material'].queryset = items_ativos


MaterialReportFormset = inlineformset_factory(
    Report,
    MaterialReport,
    form=MaterialReportForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)
