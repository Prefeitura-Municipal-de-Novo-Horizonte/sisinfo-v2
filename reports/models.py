"""
Modelos do app Reports - Laudos, Notas Fiscais, Empenhos e Entregas.
"""
from datetime import date, datetime
from decimal import Decimal

from django.db import models
from django.shortcuts import resolve_url as r
from django.template.defaultfilters import slugify
from django.utils import timezone


from authenticate.models import ProfessionalUser
from bidding_supplier.models import Supplier
from bidding_procurement.models import Material, MaterialBidding
from organizational_structure.models import Sector


class Report(models.Model):
    """
    Representa um laudo técnico.
    
    O status do laudo é controlado manualmente pelo usuário.
    O fechamento automático pode ser implementado futuramente
    baseado em critérios específicos (ex: todos materiais comprados).
    """
    STATUS_CHOICES = (
        ('1', 'Aberto'),
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
    file = models.CharField(
        'arquivo', max_length=255, blank=True, null=True,
        help_text='Path do arquivo no Supabase Storage ou URL')
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

