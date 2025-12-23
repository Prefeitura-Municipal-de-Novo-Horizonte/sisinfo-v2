"""
Views para o sistema de Fichas de Entrega.
Refatorado para novo fluxo: criar → gerar PDF → registrar recebimento.
"""
import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.utils import timezone
from decouple import config

from fiscal.models import DeliveryNote, DeliveryNoteItem, Invoice
from fiscal.forms import DeliveryNoteForm, RegisterReceiptForm
from fiscal.services.pdf import DeliveryNotePDFGenerator


class DeliveryNoteListView(LoginRequiredMixin, ListView):
    """Lista todas as fichas de entrega."""
    model = DeliveryNote
    template_name = 'fiscal/delivery/list.html'
    context_object_name = 'deliveries'
    paginate_by = 20
    login_url = 'authenticate:login'
    
    def get_queryset(self):
        return DeliveryNote.objects.select_related(
            'invoice__supplier', 'sector', 'delivered_by'
        ).prefetch_related('items').all()


class DeliveryNoteDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma ficha de entrega."""
    model = DeliveryNote
    template_name = 'fiscal/delivery/detail.html'
    context_object_name = 'delivery'
    login_url = 'authenticate:login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related(
            'invoice_item__material_bidding__material'
        ).all()
        return context


@login_required(login_url='authenticate:login')
def delivery_create(request, invoice_pk):
    """
    Cria uma nova ficha de entrega para uma nota fiscal.
    Novo fluxo: TODOS os itens da NF são incluídos automaticamente.
    """
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    if request.method == 'POST':
        form = DeliveryNoteForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.invoice = invoice
            delivery.delivered_by = request.user
            delivery.status = 'P'  # Pendente
            delivery.save()
            
            # Incluir TODOS os itens da nota fiscal automaticamente
            for invoice_item in invoice.items.all():
                DeliveryNoteItem.objects.create(
                    delivery_note=delivery,
                    invoice_item=invoice_item,
                    quantity_delivered=invoice_item.quantity
                )
            
            messages.success(request, 'Ficha de entrega criada! Agora você pode gerar o PDF para assinatura.')
            return redirect(reverse('fiscal:delivery_detail', kwargs={'pk': delivery.pk}))
    else:
        form = DeliveryNoteForm()
        # Se a nota tem laudo vinculado, pré-selecionar o setor
        if hasattr(invoice, 'report_link') and invoice.report_link:
            report = invoice.report_link.report
            if report.sector:
                form.initial['sector'] = report.sector
    
    context = {
        'form': form,
        'invoice': invoice,
    }
    return render(request, 'fiscal/delivery/create.html', context)


@login_required(login_url='authenticate:login')
def register_receipt(request, pk):
    """
    Registra o recebimento de uma entrega (passo 2).
    Preenche nome/data do recebedor e faz upload do documento assinado.
    """
    delivery = get_object_or_404(DeliveryNote, pk=pk)
    
    # Verificar se já foi concluída
    if delivery.is_completed:
        messages.warning(request, 'Esta entrega já foi concluída.')
        return redirect(reverse('fiscal:delivery_detail', kwargs={'pk': pk}))
    
    if request.method == 'POST':
        form = RegisterReceiptForm(request.POST, request.FILES, instance=delivery)
        if form.is_valid():
            # Upload do documento assinado para Supabase
            signed_file = request.FILES.get('signed_document_file')
            if signed_file:
                file_path = upload_signed_document(signed_file, delivery.pk)
                if file_path:
                    delivery.signed_document = file_path
            
            delivery.status = 'C'  # Concluída
            delivery.save()
            
            messages.success(request, 'Recebimento registrado com sucesso!')
            return redirect(reverse('fiscal:delivery_detail', kwargs={'pk': pk}))
    else:
        form = RegisterReceiptForm(instance=delivery)
    
    context = {
        'form': form,
        'delivery': delivery,
    }
    return render(request, 'fiscal/delivery/register_receipt.html', context)


def upload_signed_document(file, delivery_pk):
    """
    Faz upload do documento assinado para Supabase Storage.
    Retorna o path do arquivo ou None em caso de erro.
    """
    import requests
    
    supabase_url = config('SUPABASE_URL', default='')
    service_role_key = config('SUPABASE_SERVICE_ROLE_KEY', default='')
    
    if not supabase_url or not service_role_key:
        return None
    
    # Gerar nome único para o arquivo
    file_ext = file.name.split('.')[-1] if '.' in file.name else 'jpg'
    file_name = f"{delivery_pk}_{uuid.uuid4().hex[:8]}.{file_ext}"
    
    try:
        # Upload para Supabase Storage
        upload_url = f"{supabase_url}/storage/v1/object/delivery-documents/{file_name}"
        
        headers = {
            'Authorization': f'Bearer {service_role_key}',
            'Content-Type': file.content_type or 'image/jpeg',
        }
        
        response = requests.post(upload_url, headers=headers, data=file.read())
        
        if response.status_code in [200, 201]:
            return file_name
        else:
            return None
            
    except Exception:
        return None


@login_required(login_url='authenticate:login')
def delivery_generate_pdf(request, pk):
    """Gera PDF da ficha de entrega usando Browserless.io."""
    delivery = get_object_or_404(
        DeliveryNote.objects.select_related(
            'invoice__supplier', 'sector', 'delivered_by'
        ).prefetch_related('items__invoice_item__material_bidding__material'),
        pk=pk
    )
    
    try:
        pdf_bytes = DeliveryNotePDFGenerator.generate_delivery_pdf(delivery)
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="ficha_entrega_{delivery.pk}.pdf"'
        return response
    except Exception as e:
        messages.error(request, f'Erro ao gerar PDF: {str(e)}')
        return redirect(reverse('fiscal:delivery_detail', kwargs={'pk': pk}))
