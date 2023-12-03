from datetime import datetime

from django.db import models
from django.shortcuts import resolve_url as r
from django.template.defaultfilters import slugify

from authenticate.models import ProfessionalUser
from dashboard.models import Material, Sector


# Create your models here.
class Report(models.Model):
    KINDS = (('1', 'Aguardando ...'), ('2', 'Finalizado'))
    number_report = models.CharField(
        'identificação do laudo', max_length=20, unique=True, blank=True, null=True)
    slug = models.SlugField('slug')
    sector = models.ForeignKey(
        Sector, verbose_name='setor', on_delete=models.SET_NULL, blank=True, null=True)
    employee = models.CharField('funcionario', max_length=200, blank=True)
    status = models.CharField('status', max_length=1, default=1, choices=KINDS)
    justification = models.TextField('justificativa')
    professional = models.ForeignKey(
        ProfessionalUser, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='profissional', related_name='profissional')
    pro_accountable = models.ForeignKey(
        ProfessionalUser, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='profissional responsável', related_name='responsável')
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'laudo'
        verbose_name_plural = 'laudos'

    def __str__(self):
        return self.number_report

    def get_absolute_url(self):
        return r('reports:report', slug=self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.number_report:
                self.number_report = f"{datetime.now().strftime('%Y%m%d')}{
                    self.id:06}"
            self.slug = slugify(self.number_report)
        return super().save()


class MaterialReport(models.Model):
    report = models.ForeignKey(
        Report, verbose_name='laudo', blank=True, null=True, on_delete=models.SET_NULL, related_name='laudos')
    material = models.ForeignKey(
        Material, verbose_name='material', blank=True, null=True, on_delete=models.SET_NULL, related_name='materiais')
    quantity = models.IntegerField(
        'quantidade', blank=True, null=True, default=1)
    unitary_value = models.DecimalField(
        "valor", max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'materiais do laudo'
        verbose_name_plural = 'materiais do laudo'

    def save(self, *args, **kwargs):
        pass
