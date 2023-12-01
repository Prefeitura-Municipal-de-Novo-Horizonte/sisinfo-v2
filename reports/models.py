from random import choices

from django.db import models


# Create your models here.
class Reports(models.Model):
    KINDS = (('1', 'Aguardando ...'), ('2', 'Finalizado'))
    number_report = models.CharField(
        'identificação do laudo', max_length=20, unique=True, blank=True, null=True)
    sector = models.ForeignKey(
        'Sector', verbose_name='setor', on_delete=models.SET_NULL, blank=True, null=True)
    employee = models.CharField('funcionario', max_length=200, blank=True)
    status = models.Charfield('status', max_lenght=1, default=1, choices=KINDS)
