from django.db import models
from django.shortcuts import resolve_url as r
from django.template.defaultfilters import slugify

from bidding_supplier.managers import KindContactQuerySet


# Create your models here.
class Supplier(models.Model):
    company = models.CharField(
        'Razão social', max_length=200, blank=True, unique=True)
    trade = models.CharField(
        'nome fantasia', max_length=255, blank=True, null=True)
    cnpj = models.CharField('CNPJ', max_length=14, blank=True)
    slug = models.SlugField('slug')
    address = models.TextField('endereço', blank=True, null=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    update_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'fornecedor'
        verbose_name_plural = 'fornecedores'

    def __str__(self):
        return self.trade

    def get_absolute_url(self):
        return r('speaker_detail', slug=self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            if not self.trade:
                self.trade = self.company
            self.slug = slugify(self.trade)
        return super().save()


class Contact(models.Model):
    EMAIL = 'E'
    PHONE = 'P'
    KINDS = (
        (EMAIL, 'Email'),
        (PHONE, 'Telefone')
    )
    supplier = models.ForeignKey(
        'Supplier', on_delete=models.CASCADE, verbose_name='fornecedor', related_name='suppliers')
    kind = models.CharField('tipo', max_length=1, choices=KINDS)
    value = models.CharField('contato', max_length=255)
    whatsapp = models.BooleanField('whatsapp', default=False)

    objects = KindContactQuerySet.as_manager()

    class Meta:
        verbose_name = 'contato'
        verbose_name_plural = 'contatos'

    def __str__(self):
        return self.value
