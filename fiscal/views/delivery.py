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
        queryset = DeliveryNote.objects.select_related(
            'invoice__supplier', 'sector', 'delivered_by'
        ).prefetch_related('items').order_by('-created_at')
        
        # Filtros
        q = self.request.GET.get('q')
        status = self.request.GET.get('status')
        date_min = self.request.GET.get('date_min')
        date_max = self.request.GET.get('date_max')
        
        if q:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(sector__name__icontains=q) |
                Q(invoice__number__icontains=q)
            )
        
        if status:
            queryset = queryset.filter(status=status)
            
        if date_min:
            queryset = queryset.filter(created_at__date__gte=date_min)
            
        if date_max:
            queryset = queryset.filter(created_at__date__lte=date_max)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passar filtros atuais para o template
        context['current_q'] = self.request.GET.get('q', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_date_min'] = self.request.GET.get('date_min', '')
        context['current_date_max'] = self.request.GET.get('date_max', '')
        return context


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
    Envia email de notificação para Patrimônio e TI.
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
            
            # Enviar email de notificação para Patrimônio e TI
            from fiscal.services.email import send_delivery_notification
            email_sent, email_msg = send_delivery_notification(delivery)
            
            if email_sent:
                messages.success(request, f'Recebimento registrado! {email_msg}')
            else:
                messages.success(request, 'Recebimento registrado com sucesso!')
                messages.warning(request, f'Não foi possível enviar email: {email_msg}')
            
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
    Se o arquivo for um PDF, converte a primeira página para imagem JPEG.
    Retorna o path do arquivo ou None em caso de erro.
    """
    import requests
    from io import BytesIO
    
    supabase_url = config('SUPABASE_URL', default='')
    service_role_key = config('SUPABASE_SERVICE_ROLE_KEY', default='')
    
    if not supabase_url or not service_role_key:
        return None
    
    try:
        # Verificar se é PDF para converter para imagem
        content_type = file.content_type or ''
        is_pdf = content_type == 'application/pdf' or file.name.lower().endswith('.pdf')
        
        if is_pdf:
            # Converter PDF para imagem usando pypdfium2 (sem dependência de poppler)
            import pypdfium2 as pdfium
            
            pdf_bytes = file.read()
            pdf = pdfium.PdfDocument(pdf_bytes)
            
            if len(pdf) == 0:
                print("ERROR: PDF vazio ou inválido")
                return None
            
            # Renderizar primeira página (escala 2 para boa qualidade)
            page = pdf[0]
            bitmap = page.render(scale=2)
            pil_image = bitmap.to_pil()
            
            # Salvar como JPEG
            img_buffer = BytesIO()
            pil_image.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            file_data = img_buffer.read()
            file_ext = 'jpg'
            content_type = 'image/jpeg'
            
            # Fechar PDF
            pdf.close()
        else:
            # É uma imagem, usar diretamente
            file_data = file.read()
            file_ext = file.name.split('.')[-1] if '.' in file.name else 'jpg'
        
        # Gerar nome único para o arquivo
        file_name = f"{delivery_pk}_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        # Nome do bucket parametrizado
        bucket_name = config('SUPABASE_DELIVERY_BUCKET', default='delivery-documents')
        
        # Upload para Supabase Storage
        upload_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{file_name}"
        
        headers = {
            'Authorization': f'Bearer {service_role_key}',
            'Content-Type': content_type,
        }
        
        response = requests.post(upload_url, headers=headers, data=file_data)
        
        if response.status_code in [200, 201]:
            print(f"DEBUG: Upload de ficha de entrega OK: {file_name}")
            return file_name
        else:
            print(f"ERROR: Falha no upload para Supabase ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        print(f"EXCEPTION: Erro ao processar upload de ficha de entrega: {e}")
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
        # Se o status for pendente, atualiza para "A Caminho" ao gerar a ficha
        if delivery.status == 'P':
            delivery.status = 'A'
            delivery.save(update_fields=['status'])
        
        pdf_bytes = DeliveryNotePDFGenerator.generate_delivery_pdf(delivery)
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="ficha_entrega_{delivery.pk}.pdf"'
        return response
    except Exception as e:
        messages.error(request, f'Erro ao gerar PDF: {str(e)}')
        return redirect(reverse('fiscal:delivery_detail', kwargs={'pk': pk}))


@login_required(login_url='authenticate:login')
def resend_delivery_email(request, pk):
    """Reenvia email de notificação para entregas já concluídas."""
    delivery = get_object_or_404(DeliveryNote, pk=pk)
    
    # Verificar se a entrega está concluída
    if not delivery.is_completed:
        messages.warning(request, 'Apenas entregas concluídas podem ter o email reenviado.')
        return redirect(reverse('fiscal:delivery_detail', kwargs={'pk': pk}))
    
    # Enviar email
    from fiscal.services.email import send_delivery_notification
    email_sent, email_msg = send_delivery_notification(delivery)
    
    if email_sent:
        messages.success(request, f'Email reenviado! {email_msg}')
    else:
        messages.error(request, f'Erro ao reenviar email: {email_msg}')
    
    return redirect(reverse('fiscal:delivery_detail', kwargs={'pk': pk}))
