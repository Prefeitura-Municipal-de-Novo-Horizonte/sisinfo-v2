from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from authenticate.models import ProfessionalUser
from bidding_procurement.models import MaterialBidding
from bidding_supplier.models import Supplier
from organizational_structure.models import Sector
from reports.models import Report

# Importar do próprio app fiscal
from fiscal.models import Invoice, InvoiceItem, Commitment, DeliveryNote, DeliveryNoteItem

# Classes CSS padrão para inputs
STANDARD_INPUT_CLASS = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-500 focus:border-brand-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-brand-500 dark:focus:border-brand-500"
TEXTAREA_CLASS = "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"


################################
## Notas Fiscais ###############
################################

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
    """
    Formulário para cadastro/edição de Empenho.
    Usado inline na visualização da Nota Fiscal.
    """
    
    class Meta:
        model = Commitment
        fields = ['number']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['number'].widget.attrs['class'] = STANDARD_INPUT_CLASS
        self.fields['number'].widget.attrs['placeholder'] = 'Ex: 2024/00123'


################################
## Fichas de Entrega ###########
################################
class DeliveryNoteForm(forms.ModelForm):
    """Formulário para criar Ficha de Entrega."""
    
    class Meta:
        model = DeliveryNote
        fields = ['invoice', 'sector', 'received_by', 'received_at', 'observations']
    
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
