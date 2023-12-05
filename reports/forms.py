from django import forms
from django.forms import inlineformset_factory

from authenticate.models import ProfessionalUser
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
            field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
            if field in [self.fields["professional"]]:
                field.widget.attrs['disabled'] = 'disabled'
                field.widget.attrs['value'] = self.request.user.id
                field.widget.attrs['selected'] = self.request.user.id
                field.widget.attrs['data-placeholder'] = self.request.user
                field.initial = self.request.user.id
            if field in [self.fields["pro_accountable"]]:
                if self.request.user.is_tech is True:
                    field.widget.attrs['disabled'] = 'disabled'
                    field.widget.attrs['value'] = self.request.user.id
                    field.widget.attrs['selected'] = self.request.user.id
                    field.widget.attrs['data-placeholder'] = self.request.user
                    field.initial = self.request.user.id
                else:
                    professional = ProfessionalUser.objects.filter(
                        is_tech=True)
                    field.queryset = professional
