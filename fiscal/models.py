"""
Modelos do sistema fiscal (Notas, Empenhos, Entrega).
"""
import uuid
from decimal import Decimal
from django.db import models
from django.shortcuts import resolve_url as r
from django.utils import timezone

from authenticate.models import ProfessionalUser
from bidding_supplier.models import Supplier
from bidding_procurement.models import MaterialBidding
from organizational_structure.models import Sector
from reports.models import Report


class OCRJob(models.Model):
    """
    Job de processamento OCR assíncrono.
    Permite contornar o limite de 10s da Vercel dividindo o processo em múltiplas requests.
    """
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField('status', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Imagem (caminho local em media/ ou public_id do Cloudinary)
    image_path = models.CharField('caminho da imagem', max_length=500)
    
    # Hash da imagem para detecção de duplicatas (MD5)
    image_hash = models.CharField('hash da imagem', max_length=32, blank=True, db_index=True)
    
    # Resultado do OCR (JSON) - estrutura completa retornada pelo Gemini
    result = models.JSONField('resultado', null=True, blank=True)
    error_message = models.TextField('mensagem de erro', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    started_at = models.DateTimeField('iniciado em', null=True, blank=True)
    completed_at = models.DateTimeField('concluído em', null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'job de OCR'
        verbose_name_plural = 'jobs de OCR'
    
    def __str__(self):
        return f"OCR Job {self.id} ({self.get_status_display()})"
    
    def mark_processing(self):
        """Marca o job como em processamento."""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def mark_completed(self, result: dict):
        """Marca o job como concluído com sucesso."""
        self.status = 'completed'
        self.result = result
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'result', 'completed_at'])
    
    def mark_failed(self, error: str):
        """Marca o job como falhou."""
        self.status = 'failed'
        self.error_message = error
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])



class APIKeyStatus(models.Model):
    """
    Rastreia o status de quota das chaves API do Gemini.
    Usado para evitar tentativas em chaves já esgotadas no dia.
    """
    key_index = models.IntegerField('índice da chave', unique=True)
    exhausted_at = models.DateTimeField('esgotada em', null=True, blank=True)
    
    class Meta:
        verbose_name = 'status de chave API'
        verbose_name_plural = 'status de chaves API'
    
    def __str__(self):
        status = "esgotada" if self.is_exhausted_today() else "disponível"
        return f"Chave {self.key_index + 1}: {status}"
    
    def is_exhausted_today(self):
        """Verifica se a chave está esgotada hoje."""
        if not self.exhausted_at:
            return False
        return self.exhausted_at.date() == timezone.now().date()
    
    def mark_exhausted(self):
        """Marca a chave como esgotada agora."""
        self.exhausted_at = timezone.now()
        self.save(update_fields=['exhausted_at'])
    
    @classmethod
    def get_available_key_index(cls, total_keys: int) -> int | None:
        """
        Retorna o índice da primeira chave não esgotada hoje.
        Retorna None se todas estiverem esgotadas.
        """
        for i in range(total_keys):
            status, _ = cls.objects.get_or_create(key_index=i)
            if not status.is_exhausted_today():
                return i
        return None
    
    @classmethod
    def mark_key_exhausted(cls, key_index: int):
        """Marca uma chave específica como esgotada."""
        status, _ = cls.objects.get_or_create(key_index=key_index)
        status.mark_exhausted()


class StockItem(models.Model):
    """
    Representa o estoque FÍSICO de um item licitado.
    
    Diferença entre MaterialBidding e StockItem:
    - MaterialBidding.quantity: Limite total que PODE ser comprado (Contrato).
    - MaterialBidding.quantity_purchased: Total acumulado que JÁ FOI comprado (Financeiro).
    - StockItem.quantity: Saldo físico ATUAL no almoxarifado (Logística).
      (Entra com Nota Fiscal, Sai com Entrega).
    """
    material_bidding = models.OneToOneField(
        MaterialBidding, 
        on_delete=models.PROTECT,
        related_name='stock_item',
        verbose_name='material licitado'
    )
    quantity = models.IntegerField('saldo em estoque', default=0)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'item em estoque'
        verbose_name_plural = 'estoque'

    def __str__(self):
        return f"Estoque: {self.material_bidding.material.name} ({self.quantity})"


class Invoice(models.Model):
    """
    Representa uma Nota Fiscal recebida.
    """
    STATUS_CHOICES = (
        ('P', 'Pendente'),      # Nota recebida, aguardando processamento
        ('R', 'Recebida'),      # Materiais conferidos
        ('E', 'Entregue'),      # Entregue ao setor de compras
    )
    
    number = models.CharField('número da nota', max_length=20)
    supplier = models.ForeignKey(
        Supplier, verbose_name='fornecedor',
        on_delete=models.PROTECT, related_name='notas_fiscais')
    issue_date = models.DateField('data de emissão')
    access_key = models.CharField(
        'chave de acesso', max_length=44, blank=True, 
        help_text='44 dígitos da chave de acesso da NFe')
    
    # Foto da nota fiscal
    # Suporta: Supabase Storage (UUID.jpg) e Cloudinary (public_id legado)
    photo = models.CharField(
        'foto da nota', max_length=255, blank=True, null=True,
        help_text='Path da imagem (Supabase: UUID.jpg ou Cloudinary: public_id)'
    )
    
    # Controle de status
    status = models.CharField(
        'status', max_length=1, choices=STATUS_CHOICES, default='P')
    
    # Empenho (Simplificado)
    
    # Empenho (Simplificado) - Removido em favor do modelo Commitment separado
    # commitment_number = models.CharField(
    #     'número do empenho', max_length=30, blank=True)

    delivered_to_purchases = models.BooleanField(
        'entregue ao compras', default=False)
    delivered_to_purchases_at = models.DateTimeField(
        'entregue ao compras em', blank=True, null=True)
    
    observations = models.TextField('observações', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-created_at']
        verbose_name = 'nota fiscal'
        verbose_name_plural = 'notas fiscais'
        unique_together = [['number', 'supplier']]
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['issue_date']),
            models.Index(fields=['status', 'issue_date']),
        ]

    def __str__(self):
        return f"NF {self.number} - {self.supplier}"
    
    def get_absolute_url(self):
        # Vai precisar ser atualizado para 'fiscal:invoice_detail' quando movermos as views
        return r('fiscal:invoice_detail', pk=self.pk)
    
    @property
    def total_value(self):
        """
        Valor total da nota (soma dos itens).
        Otimizado: usa agregação SQL ao invés de loop Python.
        """
        from django.db.models import Sum, F
        result = self.items.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )
        return Decimal(result['total'] or 0).quantize(Decimal("0.00"))
    
    @property
    def photo_url(self):
        """
        Retorna a URL da foto correta para o ambiente.
        - Supabase Storage: UUID.jpg → URL pública do Supabase
        - Cloudinary legado: public_id → URL do Cloudinary
        - Local: local/filename → URL do media/
        """
        if not self.photo:
            return None
        
        photo_str = str(self.photo).strip()
        
        # 1. Se já é uma URL completa, retornar como está
        if photo_str.startswith('http://') or photo_str.startswith('https://'):
            return photo_str
        
        import re
        
        # 2. Se é um path do Supabase Storage (UUID.jpg)
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\\.jpg$'
        if re.match(uuid_pattern, photo_str, re.IGNORECASE):
            from decouple import config
            supabase_url = config('SUPABASE_URL', default='')
            if supabase_url:
                return f"{supabase_url}/storage/v1/object/public/ocr-images/{photo_str}"
            return None
        
        # 3. Se começa com 'local/', é arquivo local
        if photo_str.startswith('local/'):
            from django.conf import settings
            filename = photo_str.replace('local/', '')
            if not filename.lower().endswith('.jpg'):
                filename = f"{filename}.jpg"
            return f"{settings.MEDIA_URL}invoices/{filename}"
        
        # 4. Cloudinary legado (public_id como sisinfo/invoices/xxx)
        # Gerar URL do Cloudinary a partir do public_id
        if photo_str.startswith('sisinfo/') or '/' in photo_str:
            return f"https://res.cloudinary.com/dyjyzspbx/image/upload/{photo_str}"
        
        # 5. Fallback: tentar como Supabase mesmo que não case exatamente
        from decouple import config
        supabase_url = config('SUPABASE_URL', default='')
        if supabase_url:
            return f"{supabase_url}/storage/v1/object/public/ocr-images/{photo_str}"
        
        return None
    
    def mark_as_delivered_to_purchases(self):
        """Marca a nota como entregue ao setor de compras."""
        self.delivered_to_purchases = True
        self.delivered_to_purchases_at = timezone.now()
        self.status = 'E'
        self.save(update_fields=['delivered_to_purchases', 'delivered_to_purchases_at', 'status'])
    
    @property
    def has_stock_items(self):
        """
        Verifica se os materiais desta nota estão em estoque (StockItem com qty > 0).
        Otimizado: usa exists() com subquery ao invés de loop.
        """
        return StockItem.objects.filter(
            material_bidding__in=self.items.values('material_bidding'),
            quantity__gt=0
        ).exists()
    
    @property
    def has_deliveries(self):
        """Verifica se há entregas (DeliveryNote) vinculadas a esta nota."""
        return self.deliveries.exists()
    
    @property
    def delivery_process_status(self):
        """
        Retorna o status do processo de entrega para exibição na lista.
        - 'preparing': Nenhuma entrega criada.
        - 'on_way': Alguma entrega 'Pendente' ou 'A Caminho'.
        - 'delivered': Tem entregas e todas estão 'Concluída'.
        
        Otimizado: usa exists() ao invés de carregar todas as deliveries.
        """
        # Verifica se há entregas
        if not self.deliveries.exists():
            return 'preparing'
        
        # Verifica se alguma está pendente ou a caminho (1 query)
        if self.deliveries.filter(status__in=['P', 'A']).exists():
            return 'on_way'
        
        return 'delivered'


class InvoiceItem(models.Model):
    """
    Representa um item (material) de uma nota fiscal.
    """
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, 
        related_name='items', verbose_name='nota fiscal')
    material_bidding = models.ForeignKey(
        MaterialBidding, on_delete=models.PROTECT,
        verbose_name='material', related_name='itens_notas')
    quantity = models.PositiveIntegerField('quantidade')
    unit_price = models.DecimalField(
        'preço unitário', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'item da nota fiscal'
        verbose_name_plural = 'itens da nota fiscal'

    def __str__(self):
        return f"{self.material_bidding.material.name} ({self.quantity}x)"
    
    @property
    def total_price(self):
        """Valor total do item."""
        return Decimal(self.quantity * self.unit_price).quantize(Decimal("0.00"))
    
    def save(self, *args, **kwargs):
        """Ao salvar, atualiza o limite de compras do material."""
        is_new = self.pk is None
        old_quantity = 0
        
        if not is_new:
            try:
                old_item = InvoiceItem.objects.get(pk=self.pk)
                old_quantity = old_item.quantity
            except InvoiceItem.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Atualiza quantidade comprada no MaterialBidding
        quantity_diff = self.quantity - old_quantity
        if quantity_diff != 0:
            self.material_bidding.quantity_purchased = (
                self.material_bidding.quantity_purchased or 0
            ) + quantity_diff
            self.material_bidding.save(update_fields=['quantity_purchased'])





class Commitment(models.Model):
    """
    Representa um Empenho vinculado a uma nota fiscal.
    Relacionamento 1:1 com Invoice para auditoria.
    """
    invoice = models.OneToOneField(
        Invoice, on_delete=models.CASCADE,
        related_name='commitment', verbose_name='nota fiscal')
    number = models.CharField(
        'número do empenho', max_length=30, unique=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'empenho'
        verbose_name_plural = 'empenhos'

    def __str__(self):
        return f"Empenho {self.number}"


class InvoiceReportLink(models.Model):
    """
    Tabela intermediária para vincular Nota Fiscal a Laudo.
    Permite auditoria de quem/quando fez o vínculo.
    Regra: 1 Laudo -> N Notas, 1 Nota -> 1 Laudo
    """
    invoice = models.OneToOneField(
        Invoice, on_delete=models.CASCADE,
        related_name='report_link', verbose_name='nota fiscal')
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE,
        related_name='invoice_links', verbose_name='laudo')
    linked_by = models.ForeignKey(
        ProfessionalUser, on_delete=models.SET_NULL, null=True,
        related_name='invoice_report_links', verbose_name='vinculado por')
    linked_at = models.DateTimeField('vinculado em', auto_now_add=True)
    notes = models.TextField('observações', blank=True)

    class Meta:
        verbose_name = 'vínculo nota-laudo'
        verbose_name_plural = 'vínculos nota-laudo'
        ordering = ['-linked_at']

    def __str__(self):
        return f"NF {self.invoice.number} → Laudo {self.report.number_report}"


class DeliveryNote(models.Model):
    """
    Representa uma Ficha de Entrega de Material.
    
    Fluxo:
    1. Criar entrega (status='P') → gerar PDF para assinatura
    2. Registrar recebimento → preencher received_by, received_at, upload signed_document
    3. Status muda para 'C' (Concluída)
    """
    STATUS_CHOICES = (
        ('P', 'Pendente'),
        ('A', 'A Caminho'),
        ('C', 'Concluída'),
    )
    
    invoice = models.ForeignKey(
        Invoice, on_delete=models.PROTECT,
        related_name='deliveries', verbose_name='nota fiscal')
    sector = models.ForeignKey(
        Sector, on_delete=models.PROTECT,
        verbose_name='setor destinatário')
    
    # Status da entrega
    status = models.CharField(
        'status', max_length=1, choices=STATUS_CHOICES, default='P')
    
    # Quem entregou (funcionário do TI)
    delivered_by = models.ForeignKey(
        ProfessionalUser, on_delete=models.PROTECT,
        verbose_name='entregue por', related_name='entregas_realizadas')
    
    # Quem recebeu (preenchido depois da entrega física)
    received_by = models.CharField(
        'recebido por', max_length=200, blank=True)
    received_at = models.DateTimeField(
        'data/hora do recebimento', null=True, blank=True)
    
    # Endereço de entrega (digitado manualmente)
    delivery_address = models.CharField(
        'endereço de entrega', max_length=300, blank=True,
        help_text='Endereço/localização de referência para a entrega')
    
    # Documento assinado (upload para Supabase)
    signed_document = models.CharField(
        'documento assinado', max_length=255, blank=True,
        help_text='Path da imagem no Supabase (delivery-documents/)')
    
    observations = models.TextField('observações', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'ficha de entrega'
        verbose_name_plural = 'fichas de entrega'
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Entrega #{self.pk} - {self.sector}"
    
    def get_absolute_url(self):
        return r('fiscal:delivery_detail', pk=self.pk)
    
    @property
    def is_pending(self):
        """Verifica se a entrega está pendente de assinatura."""
        return self.status == 'P' or self.status == 'A'
    
    @property
    def is_completed(self):
        """Verifica se a entrega foi concluída."""
        return self.status == 'C'
    
    @property
    def signed_document_url(self):
        """Retorna a URL do documento assinado no Supabase."""
        if not self.signed_document:
            return None
        from decouple import config
        supabase_url = config('SUPABASE_URL', default='')
        if supabase_url:
            return f"{supabase_url}/storage/v1/object/public/delivery-documents/{self.signed_document}"
        return None


class DeliveryNoteItem(models.Model):
    """
    Representa um item entregue na ficha de entrega.
    """
    delivery_note = models.ForeignKey(
        DeliveryNote, on_delete=models.CASCADE,
        related_name='items', verbose_name='ficha de entrega')
    invoice_item = models.ForeignKey(
        InvoiceItem, on_delete=models.PROTECT,
        verbose_name='item da nota', related_name='entregas')
    quantity_delivered = models.PositiveIntegerField('quantidade entregue')
    
    stock_updated = models.BooleanField(
        'estoque atualizado', default=False,
        help_text='Indica se o estoque físico já foi baixado para este item'
    )

    class Meta:
        verbose_name = 'item da entrega'
        verbose_name_plural = 'itens da entrega'

    def __str__(self):
        return f"{self.invoice_item.material_bidding.material.name} ({self.quantity_delivered}x)"
