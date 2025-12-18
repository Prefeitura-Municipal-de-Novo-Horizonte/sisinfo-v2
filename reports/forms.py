from django import forms
from django.forms import inlineformset_factory

from authenticate.models import ProfessionalUser
from bidding_procurement.models import MaterialBidding
from reports.models import InterestRequestMaterial, MaterialReport, Report


# Classes CSS padrão para inputs
STANDARD_INPUT_CLASS = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-500 focus:border-brand-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-brand-500 dark:focus:border-brand-500"
TEXTAREA_CLASS = "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"


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
        
        for field_name, field in self.fields.items():
            if field_name == "justification":
                field.widget.attrs['class'] = TEXTAREA_CLASS
                field.widget.attrs['rows'] = "4"
            else:
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS

        # Configurações específicas de campos
        if "professional" in self.fields:
            professional = ProfessionalUser.objects.filter(id=self.request.user.id)
            self.fields["professional"].queryset = professional
            self.fields["professional"].initial = self.request.user.id
            self.fields["professional"].widget = forms.HiddenInput()

        if "pro_accountable" in self.fields:
            # Se é técnico ou admin, ele mesmo é o responsável (escondido)
            # Se é estagiário, deve escolher o responsável
            if self.request.user.is_tech:
                professional = ProfessionalUser.objects.filter(id=self.request.user.id)
                self.fields["pro_accountable"].queryset = professional
                self.fields["pro_accountable"].initial = self.request.user.id
                self.fields["pro_accountable"].widget = forms.HiddenInput()
            else:
                # Lista apenas técnicos como opções para responsável
                professional = ProfessionalUser.objects.filter(is_tech=True)
                self.fields["pro_accountable"].queryset = professional
                self.fields["pro_accountable"].widget.attrs['class'] = STANDARD_INPUT_CLASS


class ReportUpdateForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['sector', 'employee', 'status', 'justification']

    def clean_employee(self):
        employee = self.cleaned_data["employee"]
        words = [w.capitalize() for w in employee.split()]
        return " ".join(words)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")  # store value of request
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if field_name == "justification":
                field.widget.attrs['class'] = TEXTAREA_CLASS
                field.widget.attrs['rows'] = "4"
            else:
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS


################################
## Materiais ###################
################################
class MaterialReportForm(forms.ModelForm):
    id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = MaterialReport
        fields = ['id', 'material_bidding', 'quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            if not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS

        # Buscar materiais diretamente da tabela intermediária MaterialBidding
        # Apenas materiais com status ativo (status='1')
        items_ativos = MaterialBidding.objects.filter(
            status='1'
        ).select_related('material', 'bidding')
        
        self.fields['material_bidding'].queryset = items_ativos
        self.fields['material_bidding'].label = 'Material (Licitação)'
        
        # Customizar o label para mostrar licitações e status
        self.fields['material_bidding'].label_from_instance = self._material_label
    
    def _material_label(self, obj):
        """
        Retorna label customizado mostrando material e a licitação.
        Formato: "Material X - Licitação Y"
        """
        return f"{obj.material.name} - {obj.bidding.name}"


MaterialReportFormset = inlineformset_factory(
    Report,
    MaterialReport,
    form=MaterialReportForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)




