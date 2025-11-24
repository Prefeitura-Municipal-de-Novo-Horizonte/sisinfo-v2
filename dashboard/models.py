from decimal import Decimal

from django.db import models
from django.shortcuts import resolve_url as r
from django.template.defaultfilters import slugify

from bidding_supplier.models import Supplier


# Create your models here.
##############################################################################################
############################ SETORES E DIRETORIAS ############################################
##############################################################################################
class AbsctactDirectionSector(models.Model):
    name = models.CharField("nome", max_length=200,
                            blank=True, null=True, unique=True)
    slug = models.SlugField("slug")
    accountable = models.CharField("responsavel", max_length=200, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save()


class Direction(AbsctactDirectionSector):
    KIND = (
        ("DI", "Diretoria"),
        ("SE", "Secretária"),
        ("DE", "Departamento"),
        ("GA", "Gabinete"),
    )
    kind = models.CharField("tipo", max_length=2, choices=KIND)

    class Meta:
        ordering = ["kind", "name"]
        verbose_name = "diretoria"
        verbose_name_plural = "diretorias"

    def get_absolute_url(self):
        return r("dashboard:diretoria", slug=self.slug)


class Sector(AbsctactDirectionSector):
    direction = models.ForeignKey(
        "Direction", on_delete=models.DO_NOTHING, blank=True, verbose_name="diretoria"
    )
    phone = models.CharField("telefone", max_length=11, null=True, blank=True)
    email = models.EmailField("email", null=True, blank=True)
    address = models.TextField("endereço")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["direction", "name"]
        verbose_name = "setor"
        verbose_name_plural = "setores"

    def get_absolute_url(self):
        return r("dashboard:setor", slug=self.slug)


##############################################################################################
########################### LICITAÇÃO E SUPRIMENTOS ##########################################
##############################################################################################
STATUS_CHOICES = (("1", "Ativo"), ("2", "Inativo"))


class AbsBiddingMaterial(models.Model):
    name = models.CharField("nome", max_length=200, blank=True)
    slug = models.SlugField("slug")
    status = models.CharField(
        "status", max_length=1, blank=True, choices=STATUS_CHOICES, default=1
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.name)
    #     return super().save()


class Bidding(AbsBiddingMaterial):
    date = models.DateField("data", blank=True, null=True)

    class Meta:
        ordering = ("status", "date")
        verbose_name = "licitação"
        verbose_name_plural = "licitações"

    def get_absolute_url(self):
        return r("dashboard:licitacao", slug=self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Material(AbsBiddingMaterial):
    bidding = models.ForeignKey(
        Bidding,
        on_delete=models.SET_NULL,
        verbose_name="licitação",
        related_name="licitações",
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        "valor", max_digits=8, decimal_places=2, blank=True, null=True
    )
    readjustment = models.FloatField("reajuste", default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL,
                                 verbose_name='fornecedor', related_name='fornecedores', blank=True, null=True)

    class Meta:
        ordering = ("status", "bidding", "name")
        verbose_name = "material"
        verbose_name_plural = "materiais"

    def get_absolute_url(self):
        return r("dashboard:material", slug=self.slug)

    # @property
    def total_price(self):
        "Return o preço total com ajuste ou sem ajuste."
        if self.readjustment != 0:
            self.total_price = float(self.price) + (
                float(self.price) * (self.readjustment / 100)
            )
            return Decimal(self.total_price).quantize(Decimal("00000000.00"))
        return self.price

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            self.slug = self.slug.replace(" ", "")
            self.slug = self.slug[:10] + "-" + \
                self.supplier.slug[:10] + "-" + self.bidding.slug
        return super().save()
