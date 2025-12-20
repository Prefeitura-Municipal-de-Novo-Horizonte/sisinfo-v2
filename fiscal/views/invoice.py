"""
Views para o sistema de Notas Fiscais e Empenhos.
Refatorado do app reports para fiscal.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages import constants
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from django.db.models import Sum

# Imports do app Fiscal
# Imports do app Fiscal
from fiscal.models import Invoice, InvoiceItem, Commitment
from fiscal.forms import InvoiceForm, InvoiceItemForm, InvoiceItemFormSet, CommitmentForm

# Imports de outros apps
from bidding_procurement.models import MaterialBidding

# =====================
# NOTAS FISCAIS
# =====================

class InvoiceListView(LoginRequiredMixin, ListView):
    """Lista todas as notas fiscais."""
    model = Invoice
    template_name = 'fiscal/invoice/list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    login_url = 'authenticate:login'
    
    def get_queryset(self):
        queryset = Invoice.objects.select_related('supplier').all().order_by('-issue_date', '-created_at')
        
        # Filtros
        q = self.request.GET.get('q') # Busca por número
        if q:
            queryset = queryset.filter(number__icontains=q)
            
        supplier = self.request.GET.get('supplier') # Busca por nome do fornecedor
        if supplier:
            queryset = queryset.filter(supplier__name__icontains=supplier)

        date_min = self.request.GET.get('date_min')
        if date_min:
            queryset = queryset.filter(issue_date__gte=date_min)
            
        date_max = self.request.GET.get('date_max')
        if date_max:
            queryset = queryset.filter(issue_date__lte=date_max)

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Invoice.STATUS_CHOICES
        # Passar filtros atuais para manter estado no formulário
        context['current_status'] = self.request.GET.get('status', '')
        context['current_q'] = self.request.GET.get('q', '')
        context['current_supplier'] = self.request.GET.get('supplier', '')
        context['current_date_min'] = self.request.GET.get('date_min', '')
        context['current_date_max'] = self.request.GET.get('date_max', '')
        return context


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    """Cria uma nova nota fiscal."""
    model = Invoice
    form_class = InvoiceForm
    template_name = 'fiscal/invoice/create.html'
    login_url = 'authenticate:login'
    
    def get_success_url(self):
        messages.success(self.request, f'Nota Fiscal {self.object.number} cadastrada com sucesso!')
        # Se salvou itens automaticamente, vai para detalhes
        if self.object.items.exists():
            return reverse('fiscal:invoice_detail', kwargs={'pk': self.object.pk})
        return reverse('fiscal:invoice_items', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # 1. Vincular imagem (Supabase ou Cloudinary)
        photo_public_id = self.request.POST.get('photo_public_id')
        print(f"DEBUG InvoiceCreateView: photo_public_id recebido = '{photo_public_id}'")
        print(f"DEBUG InvoiceCreateView: self.object.photo atual = '{self.object.photo}'")
        
        if photo_public_id and not self.object.photo:
            try:
                self.object.photo = photo_public_id
                self.object.save(update_fields=['photo'])
                print(f"DEBUG InvoiceCreateView: foto salva com sucesso = '{photo_public_id}'")
            except Exception as e:
                print(f"DEBUG InvoiceCreateView: erro ao salvar foto = {e}")
        
        # 2. Processar itens vinculados via OCR
        items_saved = 0
        for key, value in self.request.POST.items():
            if key.startswith('item_material_') and value:
                try:
                    index = key.split('_')[-1]
                    material_id = value
                    
                    # Tratar valores numéricos (pt-BR)
                    qty_str = self.request.POST.get(f'item_quantity_{index}', '0').replace(',', '.')
                    price_str = self.request.POST.get(f'item_price_{index}', '0').replace(',', '.')
                    
                    quantity = float(qty_str)
                    price = float(price_str)
                    
                    if material_id and quantity > 0:
                        InvoiceItem.objects.create(
                            invoice=self.object,
                            material_bidding_id=material_id,
                            quantity=int(quantity),
                            unit_price=price
                        )
                        items_saved += 1
                except Exception as e:
                    print(f"DEBUG: Erro salvar item {key}: {e}")
        
        if items_saved > 0:
            messages.info(self.request, f'{items_saved} itens vinculados automaticamente!')
                
        return response


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de uma nota fiscal."""
    model = Invoice
    template_name = 'fiscal/invoice/detail.html'
    context_object_name = 'invoice'
    login_url = 'authenticate:login'
    
    def get_context_data(self, **kwargs):
        from fiscal.services.matching import suggest_reports_for_invoice, get_invoice_linked_report
        
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related(
            'material_bidding__material', 'material_bidding__bidding'
        ).all()
        context['deliveries'] = self.object.deliveries.select_related('sector', 'delivered_by').all()
        
        # Laudo vinculado (via InvoiceReportLink)
        context['linked_report'] = get_invoice_linked_report(self.object)
        
        # Sugestões de laudos (se não estiver vinculada)
        if not context['linked_report']:
            context['report_suggestions'] = suggest_reports_for_invoice(self.object, limit=5)
        else:
            context['report_suggestions'] = []
        
        return context


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    """Atualiza uma nota fiscal."""
    model = Invoice
    form_class = InvoiceForm
    template_name = 'fiscal/invoice/create.html'
    login_url = 'authenticate:login'
    
    def get_success_url(self):
        messages.success(self.request, f'Nota Fiscal {self.object.number} atualizada com sucesso!')
        return reverse('fiscal:invoice_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    """Exclui uma nota fiscal."""
    model = Invoice
    template_name = 'fiscal/invoice/confirm_delete.html'
    success_url = reverse_lazy('fiscal:invoices')
    login_url = 'authenticate:login'
    
    def form_valid(self, form):
        # A deleção da imagem é feita automaticamente pelo signal post_delete
        messages.success(self.request, f'Nota fiscal {self.object.number} excluída com sucesso!')
        return super().form_valid(form)


@login_required(login_url='authenticate:login')
def invoice_add_items(request, pk):
    """Adiciona itens à nota fiscal."""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Itens adicionados com sucesso!')
            return redirect(reverse('fiscal:invoice_detail', kwargs={'pk': pk}))
        else:
            messages.error(request, 'Erro ao adicionar itens. Verifique os dados.')
    else:
        formset = InvoiceItemFormSet(instance=invoice)
        # Passa o fornecedor para filtrar materiais
        for form in formset:
            form.fields['material_bidding'].queryset = MaterialBidding.objects.filter(
                supplier=invoice.supplier,
                status='1'
            ).select_related('material', 'bidding').order_by('material__name')
    
    context = {
        'invoice': invoice,
        'formset': formset,
    }
    return render(request, 'fiscal/invoice/add_items.html', context)


@login_required(login_url='authenticate:login')
def invoice_mark_delivered(request, pk):
    """Marca a nota como entregue ao setor de compras."""
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.mark_as_delivered_to_purchases()
    messages.success(request, f'Nota {invoice.number} marcada como entregue ao compras.')
    return redirect(reverse('fiscal:invoice_detail', kwargs={'pk': pk}))


@login_required(login_url='authenticate:login')
def invoice_set_commitment(request, pk):
    """
    Salva o número do empenho inline na nota fiscal.
    Cria ou atualiza o Commitment vinculado à Invoice.
    """
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if request.method == 'POST':
        commitment_number = request.POST.get('commitment_number', '').strip()
        
        if commitment_number:
            # Criar ou atualizar o Commitment
            commitment, created = Commitment.objects.update_or_create(
                invoice=invoice,
                defaults={'number': commitment_number}
            )
            action = 'cadastrado' if created else 'atualizado'
            messages.success(request, f'Empenho {commitment_number} {action} com sucesso!')
        else:
            # Se vazio, remover o commitment existente
            try:
                invoice.commitment.delete()
                messages.info(request, 'Empenho removido.')
            except Commitment.DoesNotExist:
                pass
    
    return redirect(reverse('fiscal:invoice_detail', kwargs={'pk': pk}))


@login_required(login_url='authenticate:login')
def invoice_link_report(request, pk, report_pk):
    """
    Vincula uma Nota Fiscal a um Laudo.
    Cria um InvoiceReportLink com auditoria de quem/quando vinculou.
    """
    from fiscal.models import InvoiceReportLink
    from reports.models import Report
    from fiscal.services.report_sync import check_and_close_report_if_complete
    
    invoice = get_object_or_404(Invoice, pk=pk)
    report = get_object_or_404(Report, pk=report_pk)
    
    # Verificar se já existe vínculo
    if hasattr(invoice, 'report_link'):
        messages.warning(request, f'Esta nota já está vinculada ao laudo {invoice.report_link.report.number_report}')
        return redirect(reverse('fiscal:invoice_detail', kwargs={'pk': pk}))
    
    # Criar vínculo
    InvoiceReportLink.objects.create(
        invoice=invoice,
        report=report,
        linked_by=request.user,
        notes=''
    )
    
    # Verificar se todos os materiais do laudo já foram atendidos
    # (têm notas fiscais vinculadas com os mesmos materiais)
    report_was_closed = False
    try:
        report_was_closed = check_and_close_report_if_complete(report)
    except Exception as e:
        # Log do erro mas não impede o vínculo
        pass
    
    if report_was_closed:
        messages.success(
            request, 
            f'Nota vinculada ao laudo {report.number_report} com sucesso! '
            f'✨ Laudo fechado automaticamente (todos os materiais atendidos).'
        )
    else:
        messages.success(request, f'Nota vinculada ao laudo {report.number_report} com sucesso!')
    
    return redirect(reverse('fiscal:invoice_detail', kwargs={'pk': pk}))


@login_required(login_url='authenticate:login')
def invoice_unlink_report(request, pk):
    """
    Remove o vínculo entre Nota Fiscal e Laudo.
    Se o laudo estava fechado e agora ficou incompleto, reabre automaticamente.
    """
    from fiscal.models import InvoiceReportLink
    from fiscal.services.report_sync import check_report_still_complete
    
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if hasattr(invoice, 'report_link'):
        report = invoice.report_link.report
        report_number = report.number_report
        was_closed = report.status == '3'
        
        # Remove o vínculo
        invoice.report_link.delete()
        
        # Verifica se o laudo precisa ser reaberto
        # (se estava fechado e agora não tem mais todos os materiais cobertos)
        report_was_reopened = False
        if was_closed:
            # Checa se ainda está completo após remover esta nota
            still_complete = check_report_still_complete(report)
            if not still_complete:
                report.status = '1'  # Reabrir
                report.save(update_fields=['status'])
                report_was_reopened = True
        
        if report_was_reopened:
            messages.info(
                request, 
                f'Vínculo com laudo {report_number} removido. '
                f'⚠️ Laudo reaberto (materiais pendentes).'
            )
        else:
            messages.info(request, f'Vínculo com laudo {report_number} removido.')
    else:
        messages.warning(request, 'Esta nota não está vinculada a nenhum laudo.')
    
    return redirect(reverse('fiscal:invoice_detail', kwargs={'pk': pk}))


# =====================
# API para autocomplete
# =====================

@login_required(login_url='authenticate:login')
def api_materials_by_supplier(request):
    """API para buscar materiais de um fornecedor com info de limite disponível."""
    supplier_id = request.GET.get('supplier_id')
    
    if not supplier_id:
        return JsonResponse({'materials': []})
    
    materials = MaterialBidding.objects.filter(
        supplier_id=supplier_id,
        status='1'
    ).select_related('material', 'bidding')
    
    result = []
    for m in materials:
        result.append({
            'id': m.id,
            'name': f"{m.material.name} - {m.bidding.name}",
            'price': str(m.price),
            'available': m.available_for_purchase,
            'usage_percent': m.usage_percentage,
            'is_near_limit': m.is_near_limit,
        })
    
    return JsonResponse({'materials': result})


# =====================
# UPLOAD E OCR
# =====================

@login_required(login_url='authenticate:login')
def invoice_upload(request):
    """Página de upload de nota fiscal."""
    return render(request, 'fiscal/invoice/upload.html')


# Função invoice_process removida
# OCR agora é assíncrono via Supabase Edge Functions (ver fiscal/views/ocr.py)




# =====================
# EMPENHOS
# =====================

class CommitmentListView(LoginRequiredMixin, ListView):
    """Lista todos os empenhos com paginação."""
    model = Commitment
    template_name = 'fiscal/commitment/list.html'
    context_object_name = 'commitments'
    paginate_by = 20
    login_url = 'authenticate:login'
    
    def get_queryset(self):
        return Commitment.objects.select_related(
            'invoice__supplier', 'invoice__report_link__report__sector'
        ).order_by('-created_at')


class CommitmentCreateView(LoginRequiredMixin, CreateView):
    """Cria um novo empenho."""
    model = Commitment
    form_class = CommitmentForm
    template_name = 'fiscal/commitment/create.html'
    login_url = 'authenticate:login'
    
    def get_success_url(self):
        messages.success(self.request, f'Empenho {self.object.number} cadastrado com sucesso!')
        return reverse('fiscal:commitments')
    
    def get_initial(self):
        initial = super().get_initial()
        # Se veio de uma nota fiscal, pré-selecionar
        invoice_pk = self.request.GET.get('invoice')
        if invoice_pk:
            initial['invoice'] = invoice_pk
        return initial


class CommitmentDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes de um empenho."""
    model = Commitment
    template_name = 'fiscal/commitment/detail.html'
    context_object_name = 'commitment'
    login_url = 'authenticate:login'


class CommitmentUpdateView(LoginRequiredMixin, UpdateView):
    """Atualiza um empenho."""
    model = Commitment
    form_class = CommitmentForm
    template_name = 'fiscal/commitment/create.html'
    login_url = 'authenticate:login'
    
    def get_success_url(self):
        messages.success(self.request, f'Empenho {self.object.number} atualizado com sucesso!')
        return reverse('fiscal:commitment_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context
