from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from authenticate.models import ProfessionalUser
from bidding_procurement.models import MaterialBidding
from bidding_supplier.models import Supplier
from core.constants import STANDARD_INPUT_CLASS, TEXTAREA_CLASS
from organizational_structure.models import Sector
from reports.models import Report

# Importar do próprio app fiscal
from fiscal.models import Invoice, InvoiceItem, Commitment, DeliveryNote, DeliveryNoteItem


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
    """Formulário para criar Ficha de Entrega (passo 1 - só setor)."""
    
    class Meta:
        model = DeliveryNote
        fields = ['sector', 'observations']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if field_name == 'observations':
                field.widget.attrs['class'] = TEXTAREA_CLASS
                field.widget.attrs['rows'] = '3'
                field.widget.attrs['placeholder'] = 'Observações (opcional)'
            else:
                field.widget.attrs['class'] = STANDARD_INPUT_CLASS
        
        self.fields['sector'].queryset = Sector.objects.all().order_by('name')


class RegisterReceiptForm(forms.ModelForm):
    """Formulário para registrar recebimento (passo 2 - após entrega física)."""
    
    signed_document_file = forms.FileField(
        label='Documento assinado',
        required=True,
        help_text='Foto, scan ou PDF do documento de entrega assinado'
    )
    
    class Meta:
        model = DeliveryNote
        fields = ['received_by', 'received_at', 'delivery_address']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['received_by'].widget.attrs['class'] = STANDARD_INPUT_CLASS
        self.fields['received_by'].widget.attrs['placeholder'] = 'Nome de quem recebeu'
        self.fields['received_by'].required = True
        
        self.fields['received_at'].widget = forms.DateTimeInput(attrs={
            'class': STANDARD_INPUT_CLASS,
            'type': 'datetime-local',
        })
        self.fields['received_at'].required = True
        
        self.fields['delivery_address'].widget.attrs['class'] = STANDARD_INPUT_CLASS
        self.fields['delivery_address'].widget.attrs['placeholder'] = 'Ex: Prédio da Prefeitura, Sala 101'
        
        self.fields['signed_document_file'].widget.attrs['class'] = STANDARD_INPUT_CLASS
        self.fields['signed_document_file'].widget.attrs['accept'] = 'image/*,.pdf,application/pdf'
        
        # Define data/hora atual como padrão
        if not self.instance.received_at:
            self.initial['received_at'] = timezone.now().strftime('%Y-%m-%dT%H:%M')
    
    def clean_signed_document_file(self):
        """Valida que o arquivo é uma imagem ou PDF."""
        file = self.cleaned_data.get('signed_document_file')
        if file:
            content_type = file.content_type
            valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf']
            if content_type not in valid_types:
                raise forms.ValidationError(
                    'Formato de arquivo inválido. Envie uma imagem (JPG, PNG, GIF) ou PDF.'
                )
        return file



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
