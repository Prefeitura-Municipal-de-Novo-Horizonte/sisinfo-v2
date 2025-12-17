"""
Modelos do app Reports - Laudos, Notas Fiscais, Empenhos e Entregas.
"""
from datetime import date, datetime
from decimal import Decimal

from django.db import models
from django.shortcuts import resolve_url as r
from django.template.defaultfilters import slugify
from django.utils import timezone

from cloudinary.models import CloudinaryField

from authenticate.models import ProfessionalUser
from bidding_supplier.models import Supplier
from bidding_procurement.models import Material, MaterialBidding
from organizational_structure.models import Sector
from reports.managers import KindInterestRequestMaterialQuerySet


class Report(models.Model):
    """
    Representa um laudo técnico.
    
    O status do laudo é controlado manualmente pelo usuário.
    O fechamento automático pode ser implementado futuramente
    baseado em critérios específicos (ex: todos materiais comprados).
    """
    STATUS_CHOICES = (
        ('1', 'Aberto'),
        ('2', 'Aguardando'),
        ('3', 'Finalizado')
    )

    number_report = models.CharField(
        'identificação do laudo', max_length=20, unique=True, blank=True, null=True)
    slug = models.SlugField('slug')
    sector = models.ForeignKey(
        Sector, verbose_name='setor', on_delete=models.SET_NULL, blank=True, null=True)
    employee = models.CharField('funcionario', max_length=200, blank=True)
    status = models.CharField('status', max_length=1, default='1', choices=STATUS_CHOICES)
    justification = models.TextField('justificativa')
    professional = models.ForeignKey(
        ProfessionalUser, on_delete=models.DO_NOTHING, 
        verbose_name='profissional', related_name='laudos_criados')
    pro_accountable = models.ForeignKey(
        ProfessionalUser, on_delete=models.DO_NOTHING, 
        verbose_name='profissional responsável', related_name='laudos_responsavel')
    
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['-created_at', 'status', '-updated_at']
        verbose_name = 'laudo'
        verbose_name_plural = 'laudos'

    def __str__(self):
        return self.number_report or f"Laudo #{self.pk}"

    def get_absolute_url(self):
        """Retorna a URL absoluta para visualização do laudo."""
        return r('reports:report_view', slug=self.slug)


class MaterialReport(models.Model):
    """
    Representa um material incluído em um laudo.
    """
    report = models.ForeignKey(
        Report, verbose_name='laudo', blank=True, null=True, 
        on_delete=models.CASCADE, related_name='materiais')
    material_bidding = models.ForeignKey(
        MaterialBidding, verbose_name='material da licitação', 
        blank=True, null=True, on_delete=models.SET_NULL, 
        related_name='materiais_laudos')
    quantity = models.PositiveIntegerField('quantidade', default=1)
    unitary_price = models.DecimalField(
        "valor", max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'material do laudo'
        verbose_name_plural = 'materiais do laudo'

    def __str__(self):
        if self.material_bidding:
            return f"{self.material_bidding.material.name} ({self.quantity}x)"
        return f"Material #{self.pk}"

    @property
    def total_price(self):
        """Calcula o preço total (quantidade * preço unitário)."""
        if not self.quantity or not self.unitary_price:
            return Decimal("0.00")
        return Decimal(self.quantity * self.unitary_price).quantize(Decimal("0.00"))


class Invoice(models.Model):
    """
    Representa uma Nota Fiscal recebida.
    
    A nota fiscal pode ter uma foto (upload via Cloudinary) e
    contém itens (InvoiceItem) que são vinculados aos materiais.
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
    
    # Foto da nota fiscal (Cloudinary)
    photo = CloudinaryField(
        'foto da nota', blank=True, null=True,
        folder='sisinfo/invoices')
    
    # Controle de status
    status = models.CharField(
        'status', max_length=1, choices=STATUS_CHOICES, default='P')
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
        # Evitar duplicação de nota do mesmo fornecedor
        unique_together = [['number', 'supplier']]

    def __str__(self):
        return f"NF {self.number} - {self.supplier}"
    
    def get_absolute_url(self):
        return r('reports:invoice_detail', pk=self.pk)
    
    @property
    def total_value(self):
        """Valor total da nota (soma dos itens)."""
        total = sum(item.total_price for item in self.items.all())
        return Decimal(total).quantize(Decimal("0.00"))
    
    def mark_as_delivered_to_purchases(self):
        """Marca a nota como entregue ao setor de compras."""
        self.delivered_to_purchases = True
        self.delivered_to_purchases_at = timezone.now()
        self.status = 'E'
        self.save(update_fields=['delivered_to_purchases', 'delivered_to_purchases_at', 'status'])


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
            # Se é atualização, pega quantidade antiga para calcular diferença
            old_item = InvoiceItem.objects.get(pk=self.pk)
            old_quantity = old_item.quantity
        
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
    Representa um Empenho vinculado a um laudo e nota fiscal.
    """
    number = models.CharField(
        'número do empenho', max_length=30, unique=True)
    report = models.ForeignKey(
        Report, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='commitments', verbose_name='laudo')
    invoice = models.ForeignKey(
        Invoice, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='commitments', verbose_name='nota fiscal')
    commitment_date = models.DateField('data do empenho')
    notes = models.TextField('observações', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['-commitment_date', '-created_at']
        verbose_name = 'empenho'
        verbose_name_plural = 'empenhos'

    def __str__(self):
        return f"Empenho {self.number}"


class DeliveryNote(models.Model):
    """
    Representa uma Ficha de Entrega de Material.
    
    Gerada quando os materiais são entregues ao setor requisitante.
    Pode ser gerada como PDF para assinatura.
    """
    invoice = models.ForeignKey(
        Invoice, on_delete=models.PROTECT,
        related_name='deliveries', verbose_name='nota fiscal')
    commitment = models.ForeignKey(
        Commitment, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='deliveries', verbose_name='empenho')
    sector = models.ForeignKey(
        Sector, on_delete=models.PROTECT,
        verbose_name='setor destinatário')
    
    # Quem entregou (funcionário do TI)
    delivered_by = models.ForeignKey(
        ProfessionalUser, on_delete=models.PROTECT,
        verbose_name='entregue por', related_name='entregas_realizadas')
    
    # Quem recebeu (campo texto - pessoa do setor)
    received_by = models.CharField('recebido por', max_length=200)
    received_at = models.DateTimeField('data/hora do recebimento')
    
    observations = models.TextField('observações', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['-received_at', '-created_at']
        verbose_name = 'ficha de entrega'
        verbose_name_plural = 'fichas de entrega'

    def __str__(self):
        return f"Entrega #{self.pk} - {self.sector}"
    
    def get_absolute_url(self):
        return r('reports:delivery_detail', pk=self.pk)


class DeliveryNoteItem(models.Model):
    """
    Representa um item entregue na ficha de entrega.
    
    NOTA: A ficha de entrega é apenas um registro/documento,
    não afeta o controle de limite de compras (que é gerenciado
    apenas pelas notas fiscais).
    """
    delivery_note = models.ForeignKey(
        DeliveryNote, on_delete=models.CASCADE,
        related_name='items', verbose_name='ficha de entrega')
    invoice_item = models.ForeignKey(
        InvoiceItem, on_delete=models.PROTECT,
        verbose_name='item da nota', related_name='entregas')
    quantity_delivered = models.PositiveIntegerField('quantidade entregue')

    class Meta:
        verbose_name = 'item da entrega'
        verbose_name_plural = 'itens da entrega'

    def __str__(self):
        return f"{self.invoice_item.material_bidding.material.name} ({self.quantity_delivered}x)"


class ReportDocument(models.Model):
    """
    Representa um documento anexado ao laudo (foto escaneada, etc).
    """
    FILE_TYPES = (
        ('L', 'Laudo Escaneado'),
        ('O', 'Outro'),
    )
    
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE,
        related_name='documents', verbose_name='laudo')
    file = CloudinaryField('arquivo', folder='sisinfo/reports')
    file_type = models.CharField(
        'tipo', max_length=1, choices=FILE_TYPES, default='L')
    description = models.CharField('descrição', max_length=200, blank=True)
    uploaded_at = models.DateTimeField('enviado em', auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'documento do laudo'
        verbose_name_plural = 'documentos do laudo'

    def __str__(self):
        return f"Doc #{self.pk} - {self.report}"


# Modelo legado mantido para compatibilidade
class InterestRequestMaterial(models.Model):
    """
    Representa uma Solicitação ou Empenho de material (legado).
    
    DEPRECATED: Use o modelo Commitment para novos empenhos.
    """
    REQUEST = 'S'
    INTEREST = 'E'
    KINDS = (
        (REQUEST, 'Solicitação'),
        (INTEREST, 'Empenho'),
    )
    value = models.CharField('valor', max_length=20)
    kind = models.CharField('kind', max_length=1,
                            blank=True, null=True, choices=KINDS)
    report = models.ForeignKey(
        Report, verbose_name='laudo', blank=True, null=True, on_delete=models.SET_NULL)
    invoice = models.ForeignKey(
        Invoice, verbose_name='nota fiscal', null=True, on_delete=models.SET_NULL)

    objects = KindInterestRequestMaterialQuerySet.as_manager()

    class Meta:
        verbose_name = 'solicitação ou empenho (legado)'
        verbose_name_plural = 'solicitações ou empenhos (legado)'

    def __str__(self):
        return self.value
