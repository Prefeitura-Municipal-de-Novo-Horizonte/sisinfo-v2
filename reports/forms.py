from django import forms
from django.forms import inlineformset_factory

from authenticate.models import ProfessionalUser
from bidding_procurement.models import MaterialBidding
from reports.models import InterestRequestMaterial, Invoice, MaterialReport, Report


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


################################
## Notas Fiscais ###############
################################
from django.utils import timezone
from reports.models import Invoice, InvoiceItem, Commitment, DeliveryNote, DeliveryNoteItem
from bidding_supplier.models import Supplier
from organizational_structure.models import Sector


class InvoiceForm(forms.ModelForm):
    """Formulário para cadastro de Nota Fiscal."""
    
    class Meta:
        model = Invoice
        fields = ['number', 'supplier', 'issue_date', 'access_key', 'photo', 'observations']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if field_name == 'observations':
                field.widget.attrs['class'] = TEXTAREA_CLASS
                field.widget.attrs['rows'] = '3'
                field.widget.attrs['placeholder'] = 'Observações (opcional)'
            elif field_name == 'issue_date':
                field.widget = forms.DateInput(attrs={
                    'class': STANDARD_INPUT_CLASS,
                    'type': 'date',
                })
            elif field_name == 'photo':
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS
                field.widget.attrs['accept'] = 'image/*'
            else:
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS
        
        self.fields['supplier'].queryset = Supplier.objects.all().order_by('trade')
        self.fields['access_key'].widget.attrs['placeholder'] = '44 dígitos da chave de acesso'
        self.fields['access_key'].widget.attrs['maxlength'] = '44'
        self.fields['number'].widget.attrs['placeholder'] = 'Ex: 12345'


class InvoiceItemForm(forms.ModelForm):
    """Formulário para adicionar item à nota fiscal."""
    
    class Meta:
        model = InvoiceItem
        fields = ['material_bidding', 'quantity', 'unit_price']
    
    def __init__(self, *args, supplier=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs['class'] = STANDARD_INPUT_CLASS
        
        self.fields['quantity'].widget.attrs['min'] = '1'
        self.fields['unit_price'].widget.attrs['step'] = '0.01'
        self.fields['unit_price'].widget.attrs['min'] = '0'
        
        # Filtrar materiais pelo fornecedor da nota
        if supplier:
            self.fields['material_bidding'].queryset = MaterialBidding.objects.filter(
                supplier=supplier,
                status='1'
            ).select_related('material', 'bidding').order_by('material__name')
        else:
            self.fields['material_bidding'].queryset = MaterialBidding.objects.filter(
                status='1'
            ).select_related('material', 'bidding').order_by('material__name')
        
        # Label customizado
        self.fields['material_bidding'].label_from_instance = lambda obj: f"{obj.material.name} - {obj.bidding.name}"


InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True,
)


################################
## Empenhos ####################
################################
class CommitmentForm(forms.ModelForm):
    """Formulário para cadastro de Empenho."""
    
    class Meta:
        model = Commitment
        fields = ['number', 'report', 'invoice', 'commitment_date', 'notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if field_name == 'notes':
                field.widget.attrs['class'] = TEXTAREA_CLASS
                field.widget.attrs['rows'] = '3'
            elif field_name == 'commitment_date':
                field.widget = forms.DateInput(attrs={
                    'class': STANDARD_INPUT_CLASS,
                    'type': 'date',
                })
            else:
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS
        
        self.fields['number'].widget.attrs['placeholder'] = 'Ex: 2024/00123'
        
        # Filtrar apenas laudos ABERTOS (status='1')
        self.fields['report'].queryset = Report.objects.filter(
            status='1'
        ).order_by('-created_at')
        
        # Filtrar apenas notas fiscais não vinculadas a outros empenhos
        # Exceto a nota atual se estiver editando
        used_invoice_ids = Commitment.objects.values_list('invoice_id', flat=True)
        if self.instance.pk and self.instance.invoice_id:
            # Se está editando, permitir a nota atual
            used_invoice_ids = used_invoice_ids.exclude(pk=self.instance.pk)
        
        self.fields['invoice'].queryset = Invoice.objects.exclude(
            id__in=used_invoice_ids
        ).select_related('supplier').order_by('-issue_date')



################################
## Fichas de Entrega ###########
################################
class DeliveryNoteForm(forms.ModelForm):
    """Formulário para criar Ficha de Entrega."""
    
    class Meta:
        model = DeliveryNote
        fields = ['invoice', 'commitment', 'sector', 'received_by', 'received_at', 'observations']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if field_name == 'observations':
                field.widget.attrs['class'] = TEXTAREA_CLASS
                field.widget.attrs['rows'] = '3'
            elif field_name == 'received_at':
                field.widget = forms.DateTimeInput(attrs={
                    'class': STANDARD_INPUT_CLASS,
                    'type': 'datetime-local',
                })
            else:
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS
        
        self.fields['sector'].queryset = Sector.objects.all().order_by('name')
        self.fields['received_by'].widget.attrs['placeholder'] = 'Nome de quem está recebendo'
        
        # Define data/hora atual como padrão
        if not self.instance.pk:
            self.initial['received_at'] = timezone.now().strftime('%Y-%m-%dT%H:%M')


class DeliveryNoteItemForm(forms.ModelForm):
    """Formulário para item da ficha de entrega."""
    
    class Meta:
        model = DeliveryNoteItem
        fields = ['invoice_item', 'quantity_delivered']
    
    def __init__(self, *args, invoice=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs['class'] = STANDARD_INPUT_CLASS
        
        self.fields['quantity_delivered'].widget.attrs['min'] = '1'
        
        # Filtrar itens pela nota fiscal
        if invoice:
            self.fields['invoice_item'].queryset = InvoiceItem.objects.filter(
                invoice=invoice
            ).select_related('material_bidding__material')
            # Label customizado
            self.fields['invoice_item'].label_from_instance = lambda obj: f"{obj.material_bidding.material.name} ({obj.quantity}x)"


DeliveryNoteItemFormSet = inlineformset_factory(
    DeliveryNote,
    DeliveryNoteItem,
    form=DeliveryNoteItemForm,
    extra=1,
    can_delete=True,
)

