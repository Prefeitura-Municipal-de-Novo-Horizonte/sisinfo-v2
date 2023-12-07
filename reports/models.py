from datetime import date, datetime
from decimal import Decimal

from django.db import models
from django.shortcuts import resolve_url as r
from django.template.defaultfilters import slugify

from authenticate.models import ProfessionalUser
from bidding_supplier.models import Supplier
from dashboard.models import Material, Sector
from reports.managers import KindInterestRequestMaterialQuerySet


# Create your models here.
class Report(models.Model):
    KINDS = (('1', 'Aberto'), ('2', 'Aguardando'), ('3', 'Finalizado'))

    number_report = models.CharField(
        'identificação do laudo', max_length=20, unique=True, blank=True, null=True)
    slug = models.SlugField('slug')
    sector = models.ForeignKey(
        Sector, verbose_name='setor', on_delete=models.SET_NULL, blank=True, null=True)
    employee = models.CharField('funcionario', max_length=200, blank=True)
    status = models.CharField('status', max_length=1, default=1, choices=KINDS)
    justification = models.TextField('justificativa')
    professional = models.ForeignKey(
        ProfessionalUser, on_delete=models.DO_NOTHING, verbose_name='profissional', related_name='profissional')
    pro_accountable = models.ForeignKey(
        ProfessionalUser, on_delete=models.DO_NOTHING, verbose_name='profissional responsável', related_name='responsável')
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['-created_at', 'status', '-updated_at']
        verbose_name = 'laudo'
        verbose_name_plural = 'laudos'

    def __str__(self):
        return self.number_report

    def get_absolute_url(self):
        return r('reports:report_view', slug=self.slug)

    def save(self, *args, **kwargs):
        reports = Report.objects.filter(created_at__date=date.today()).count()
        if not self.slug:
            if not self.number_report:
                self.number_report = datetime.now().strftime('%Y%m%d') + \
                    f"{self.sector.id:03}" + f"{(reports + 1):03}"
            self.slug = slugify(self.number_report)
        return super().save()


class MaterialReport(models.Model):
    report = models.ForeignKey(
        Report, verbose_name='laudo', blank=True, null=True, on_delete=models.CASCADE, related_name='laudos')
    material = models.ForeignKey(
        Material, verbose_name='material', blank=True, null=True, on_delete=models.SET_NULL, related_name='materiais')
    quantity = models.IntegerField(
        'quantidade', blank=True, null=True, default=1)
    unitary_price = models.DecimalField(
        "valor", max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'materiais do laudo'
        verbose_name_plural = 'materiais do laudo'

    def save(self, *args, **kwargs):
        if not self.unitary_price:
            novo_decimal = Decimal(self.material.total_price())
            self.unitary_price = novo_decimal
        return super().save()

    def total_price(self):
        self.total_price = float(self.quantity) * float(self.unitary_price)
        return Decimal(self.total_price).quantize(Decimal("00000000.00"))


class Invoice(models.Model):
    note_number = models.CharField('numero da Nota', max_length=10)
    supplier = models.ForeignKey(Supplier, verbose_name='fornecedor',
                                 related_name='fornecedor', on_delete=models.SET_NULL, blank=True, null=True)
    access_key = models.CharField(
        'chave de acesso', max_length=50, blank=True, null=True)
    note_issuance_date = models.DateField('data da emissão da nota')

    class Meta:
        ordering = ('note_issuance_date', 'supplier', 'note_number')
        verbose_name = 'nota fiscal'
        verbose_name_plural = 'notas fiscais'

    def __str__(self):
        return self.note_number


class InterestRequestMaterial(models.Model):
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
        verbose_name = 'solicitação ou empenho'
        verbose_name_plural = 'solicitações ou empenhos'

    def __str__(self):
        return self.value

    def save(self, *args, **kwargs):
        self.report.status = 2
        super().save()
