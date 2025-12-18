"""
Modelos do sistema fiscal (Notas, Empenhos, Entrega).
"""
from decimal import Decimal
from django.db import models
from django.shortcuts import resolve_url as r
from django.utils import timezone
from cloudinary.models import CloudinaryField

from authenticate.models import ProfessionalUser
from bidding_supplier.models import Supplier
from bidding_procurement.models import MaterialBidding
from organizational_structure.models import Sector
from reports.models import Report


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
        unique_together = [['number', 'supplier']]

    def __str__(self):
        return f"NF {self.number} - {self.supplier}"
    
    def get_absolute_url(self):
        # Vai precisar ser atualizado para 'fiscal:invoice_detail' quando movermos as views
        return r('fiscal:invoice_detail', pk=self.pk)
    
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
        return r('fiscal:delivery_detail', pk=self.pk)


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

    class Meta:
        verbose_name = 'item da entrega'
        verbose_name_plural = 'itens da entrega'

    def __str__(self):
        return f"{self.invoice_item.material_bidding.material.name} ({self.quantity_delivered}x)"
