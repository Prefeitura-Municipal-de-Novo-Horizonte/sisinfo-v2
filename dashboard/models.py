from decimal import Decimal

from django.db import models
from django.shortcuts import reverse as r
from django.template.defaultfilters import slugify

from bidding_supplier.models import Supplier

##############################################################################################
############################ SETORES E DIRETORIAS ############################################
##############################################################################################


class AbsctractDirectionSector(models.Model):
    name = models.CharField("nome", max_length=200, blank=True)
    slug = models.SlugField("slug")
    accountable = models.CharField("responsável", max_length=200, blank=True)
    address = models.CharField("endereço", max_length=200, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save()


class Direction(AbsctractDirectionSector):
    class Meta:
        ordering = ("name",)
        verbose_name = "diretoria"
        verbose_name_plural = "diretorias"

    def get_absolute_url(self):
        return r("dashboard:diretoria", slug=self.slug)


class Sector(AbsctractDirectionSector):
    direction = models.ForeignKey(
        Direction,
        on_delete=models.SET_NULL,
        verbose_name="diretoria",
        related_name="diretorias",
        blank=True,
        null=True,
    )
    phone = models.CharField("telefone", max_length=15, blank=True, null=True)
    email = models.EmailField("email", max_length=200, blank=True, null=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "setor"
        verbose_name_plural = "setores"

    def get_absolute_url(self):
        return r("dashboard:setor", slug=self.slug)


##############################################################################################
########################### LICITAÇÃO E SUPRIMENTOS ##########################################
##############################################################################################
STATUS_CHOICES = (("1", "Ativo"), ("2", "Inativo"))


class AbsBiddingMaterial(models.Model):
    """
    Modelo abstrato base para Material e Bidding.
    
    NOTA: O campo 'status' foi removido deste modelo abstrato.
    Agora o status é gerenciado na tabela intermediária MaterialBidding,
    permitindo que um material tenha status diferentes em cada licitação.
    """
    name = models.CharField("nome", max_length=200, blank=True)
    slug = models.SlugField("slug")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Bidding(AbsBiddingMaterial):
    """
    Representa uma licitação/pregão.
    
    Não possui mais campo 'status' próprio. Cada material vinculado
    a esta licitação possui seu próprio status na tabela MaterialBidding.
    """
    date = models.DateField("data", blank=True, null=True)

    class Meta:
        ordering = ("date", "name")
        verbose_name = "licitação"
        verbose_name_plural = "licitações"

    def get_absolute_url(self):
        return r("dashboard:licitacao", slug=self.slug)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Material(AbsBiddingMaterial):
    """
    Representa um material/suprimento que pode ser usado em múltiplas licitações.
    
    A relação com Bidding é Many-to-Many através da tabela intermediária MaterialBidding.
    """
    price = models.DecimalField(
        "valor base",
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Preço base do material (sem reajuste)"
    )
    readjustment = models.FloatField(
        "reajuste padrão (%)",
        default=0,
        help_text="Percentual de reajuste aplicado sobre o preço base"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        verbose_name='fornecedor',
        related_name='materials',
        blank=True,
        null=True
    )
    
    # Many-to-Many com Bidding através de MaterialBidding
    biddings = models.ManyToManyField(
        Bidding,
        through='MaterialBidding',
        related_name='materials',
        verbose_name='licitações',
        blank=True
    )

    class Meta:
        ordering = ("name", "supplier")
        verbose_name = "material"
        verbose_name_plural = "materiais"

    def get_absolute_url(self):
        return r("dashboard:material", slug=self.slug)

    def total_price(self):
        """Retorna o preço total com reajuste aplicado."""
        if not self.price:
            return Decimal("0.00")
        
        if self.readjustment and self.readjustment != 0:
            total = float(self.price) + (float(self.price) * (self.readjustment / 100))
            return Decimal(str(total)).quantize(Decimal("0.00"))
        
        return self.price

    def save(self, *args, **kwargs):
        if not self.slug:
            # Slug baseado em nome + fornecedor (sem licitação)
            slug_base = slugify(self.name)[:20]
            
            if self.supplier:
                slug_base = f"{slug_base}-{self.supplier.slug[:15]}"
            
            # Garantir unicidade
            original_slug = slug_base
            counter = 1
            while Material.objects.filter(slug=slug_base).exclude(pk=self.pk).exists():
                slug_base = f"{original_slug}-{counter}"
                counter += 1
            
            self.slug = slug_base
        
        return super().save(*args, **kwargs)


class MaterialBidding(models.Model):
    """
    Tabela intermediária entre Material e Bidding (many-to-many).
    
    Representa a inclusão de um material específico em uma licitação,
    com status próprio e snapshot do preço no momento da vinculação.
    """
    STATUS_CHOICES = (
        ("1", "Ativo"),
        ("2", "Inativo"),
    )
    
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='bidding_associations',
        verbose_name='material'
    )
    bidding = models.ForeignKey(
        Bidding,
        on_delete=models.CASCADE,
        related_name='material_associations',
        verbose_name='licitação'
    )
    status = models.CharField(
        "status",
        max_length=1,
        choices=STATUS_CHOICES,
        default="1",
        help_text="Status deste material nesta licitação específica"
    )
    price_snapshot = models.DecimalField(
        "preço no momento da inclusão",
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Snapshot do preço do material quando foi adicionado à licitação"
    )
    created_at = models.DateTimeField("incluído em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)
    
    class Meta:
        ordering = ("bidding", "material")
        verbose_name = "material da licitação"
        verbose_name_plural = "materiais das licitações"
        unique_together = [['material', 'bidding']]
    
    def __str__(self):
        return f"{self.material.name} - {self.bidding.name}"
    
    def save(self, *args, **kwargs):
        # Captura price_snapshot automaticamente se não fornecido
        if not self.price_snapshot and self.material:
            self.price_snapshot = self.material.total_price()
        return super().save(*args, **kwargs)
