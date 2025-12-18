"""
Views para o sistema de Fichas de Entrega.
Refatorado do app reports para fiscal.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView
from django.utils import timezone

from fiscal.models import DeliveryNote, DeliveryNoteItem, Invoice, InvoiceItem
from fiscal.forms import DeliveryNoteForm
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
            'invoice', 'sector', 'delivered_by', 'commitment'
        ).all()


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
    """Cria uma nova ficha de entrega para uma nota fiscal."""
    invoice = get_object_or_404(Invoice, pk=invoice_pk)
    
    if request.method == 'POST':
        form = DeliveryNoteForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.invoice = invoice
            delivery.delivered_by = request.user
            delivery.save()
            
            # Processar itens da entrega
            item_ids = request.POST.getlist('item_id')
            quantities = request.POST.getlist('quantity_delivered')
            
            for item_id, quantity in zip(item_ids, quantities):
                if item_id and quantity and int(quantity) > 0:
                    invoice_item = get_object_or_404(InvoiceItem, pk=item_id)
                    DeliveryNoteItem.objects.create(
                        delivery_note=delivery,
                        invoice_item=invoice_item,
                        quantity_delivered=int(quantity)
                    )
            
            messages.success(request, 'Ficha de entrega criada com sucesso!')
            return redirect(reverse('fiscal:delivery_detail', kwargs={'pk': delivery.pk}))
    else:
        form = DeliveryNoteForm(initial={
            'invoice': invoice,
            'received_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        })
        # Se a nota está vinculada a um empenho, pré-selecionar
        if invoice.commitments.exists():
            form.initial['commitment'] = invoice.commitments.first()
            # Preencher o setor do laudo (via Report)
            commitment = invoice.commitments.first()
            if commitment.report and commitment.report.sector:
                form.initial['sector'] = commitment.report.sector
    
    # Itens disponíveis para entrega
    items = invoice.items.select_related('material_bidding__material').all()
    
    context = {
        'form': form,
        'invoice': invoice,
        'items': items,
    }
    return render(request, 'fiscal/delivery/create.html', context)


@login_required(login_url='authenticate:login')
def delivery_generate_pdf(request, pk):
    """Gera PDF da ficha de entrega usando Browserless.io."""
    delivery = get_object_or_404(
        DeliveryNote.objects.select_related(
            'invoice__supplier', 'sector', 'delivered_by', 'commitment__report'
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
