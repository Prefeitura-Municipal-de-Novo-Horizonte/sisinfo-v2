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
        
        # 1. Vincular imagem Cloudinary (se houver)
        photo_public_id = self.request.POST.get('photo_public_id')
        if photo_public_id and not self.object.photo:
            try:
                self.object.photo = photo_public_id
                self.object.save(update_fields=['photo'])
            except Exception:
                pass
        
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
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related(
            'material_bidding__material', 'material_bidding__bidding'
        ).all()
        context['commitments'] = self.object.commitments.select_related('report').all()
        context['deliveries'] = self.object.deliveries.select_related('sector', 'delivered_by').all()
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
            'report__sector', 'invoice__supplier'
        ).order_by('-commitment_date', '-created_at')


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
        # Se veio de um laudo, pré-selecionar
        report_pk = self.request.GET.get('report')
        if report_pk:
            initial['report'] = report_pk
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


@login_required(login_url='authenticate:login')
def invoice_process(request):
    """
    Processa upload de nota fiscal:
    1. Faz OCR (usando bytes para performance)
    2. Upload para Cloudinary em background (ou após sucesso)
    3. Retorna JSON com dados extraídos
    """
    import json
    import sys
    from io import BytesIO
    from PIL import Image
    from django.core.files.uploadedfile import InMemoryUploadedFile
    import cloudinary.uploader
    from fiscal.services.ocr import InvoiceOCRService, find_supplier_by_cnpj, find_similar_materials
    from bidding_supplier.models import Supplier
    from fiscal.models import Invoice # Import Invoice here for the duplication check

    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    photo = request.FILES.get('photo')
    if not photo:
        return JsonResponse({'error': 'Nenhuma imagem enviada'}, status=400)
    
    image_bytes = None
    
    try:
        # 0. Otimizar imagem (Redimensionar para reduzir KB)
        try:
            img = Image.open(photo)
            
            # Converter para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionar se maior que 1600px
            max_size = 1600
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size))
                
            output = BytesIO()
            img.save(output, format='JPEG', quality=85)
            output.seek(0)
            
            # Ler bytes para OCR e Upload
            image_bytes = output.getvalue()
            
            # Resetar ponteiro para uso do Django Upload
            output.seek(0)
            
        except Exception as e:
            # Fallback se falhar otimização
            photo.seek(0)
            image_bytes = photo.read()
            photo.seek(0)

        # 1. Extrair dados via OCR (Primeiro OCR, se falhar não sobe nada)
        ocr_service = InvoiceOCRService()
        extracted = ocr_service.extract_from_bytes(image_bytes, mime_type='image/jpeg')
        
        if extracted.error:
            # Verificar se é erro de quota (429)
            if '429' in extracted.error or 'RESOURCE_EXHAUSTED' in extracted.error or 'quota' in extracted.error.lower():
                return JsonResponse({
                    'error': 'Limite diário de OCR atingido',
                    'error_type': 'quota_exceeded',
                    'message': 'O limite gratuito de leituras por dia foi atingido. Você pode cadastrar a nota manualmente ou aguardar até amanhã para usar o OCR novamente.',
                    'manual_entry_url': '/reports/notas/nova/'
                }, status=429)
            
            # Verificar se todas as chaves falharam (quota ou inválidas)
            if 'chaves API falharam' in extracted.error or 'chaves falharam' in extracted.error:
                return JsonResponse({
                    'error': 'Todas as chaves API falharam',
                    'error_type': 'all_keys_failed',
                    'message': extracted.error,
                    'manual_entry_url': '/reports/notas/nova/'
                }, status=400)
            
            # Outros erros do OCR
            return JsonResponse({'error': f'Erro ao ler nota: {extracted.error}'}, status=400)
        
        # 2. Verificar duplicidade ANTES do upload
        existing = Invoice.objects.filter(
            number=extracted.number,
            supplier__cnpj__icontains=extracted.supplier_cnpj[:8] if extracted.supplier_cnpj else ''
        ).first()
        
        if existing:
            return JsonResponse({
                'error': f'Nota {extracted.number} já cadastrada para este fornecedor'
            }, status=400)

        # 3. Upload condicional (Local em dev, Cloudinary em prod)
        from django.conf import settings
        import uuid
        
        try:
            if settings.USE_CLOUDINARY:
                # PRODUÇÃO: Upload para Cloudinary
                import cloudinary.uploader
                upload_result = cloudinary.uploader.upload(
                    image_bytes,
                    folder='sisinfo/invoices',
                    resource_type='image'
                )
                photo_url = upload_result.get('secure_url')
                public_id = upload_result.get('public_id')
            else:
                # DESENVOLVIMENTO: Salvar localmente em media/invoices/
                from pathlib import Path
                
                # Criar diretório se não existir
                upload_dir = settings.MEDIA_ROOT / 'invoices'
                upload_dir.mkdir(parents=True, exist_ok=True)
                
                # Nome único para o arquivo
                file_ext = '.jpg'  # Já convertemos para JPEG na otimização
                filename = f"{uuid.uuid4()}{file_ext}"
                file_path = upload_dir / filename
                
                # Salvar arquivo
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)
                
                # URL relativa para acesso
                photo_url = f"{settings.MEDIA_URL}invoices/{filename}"
                public_id = f"local/{filename}"  # Marcador para identificar como local
                
        except Exception as e:
            return JsonResponse({'error': f'Erro no upload da imagem: {str(e)}'}, status=500)

        # 4. Buscar fornecedor pelo CNPJ
        supplier = find_supplier_by_cnpj(extracted.supplier_cnpj)
        supplier_data = None
        if supplier:
            supplier_data = {
                'id': supplier.id,
                'name': supplier.trade or supplier.company,
                'cnpj': supplier.cnpj
            }
        
        # 5. Processar materiais (busca sugestões se tiver fornecedor)
        materials_suggestions = []
        for product in extracted.products:
            suggestions = []
            if supplier:
                similar = find_similar_materials(product.description, supplier.id, limit=5)
                suggestions = [
                    {
                        'id': m.id,
                        'name': m.material.name,
                        'bidding': m.bidding.name,
                        'price': str(m.price),
                        'available': m.available_for_purchase,
                    }
                    for m in similar
                ]
            
            materials_suggestions.append({
                'product': {
                    'code': product.code,
                    'description': product.description,
                    'quantity': product.quantity,
                    'unit': product.unit,
                    'unit_price': product.unit_price,
                    'total_price': product.total_price,
                },
                'suggestions': suggestions,
                'selected_material': None # Front vai usar isso
            })
        
        # 6. Retornar dados extraídos
        return JsonResponse({
            'success': True,
            'photo_url': photo_url,
            'photo_public_id': public_id,
            'number': extracted.number,
            'series': extracted.series,
            'access_key': extracted.access_key,
            'issue_date': extracted.issue_date,
            'total_value': extracted.total_value,
            'supplier': supplier_data,
            'supplier_name_detected': extracted.supplier_name,
            'supplier_cnpj_detected': extracted.supplier_cnpj,
            'materials': materials_suggestions,
            'observations': extracted.observations,
            'confidence': extracted.confidence,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
