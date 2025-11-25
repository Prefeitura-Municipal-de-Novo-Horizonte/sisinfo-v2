from decimal import Decimal

from django.db import models
from django.shortcuts import reverse as r
from django.template.defaultfilters import slugify

from bidding_supplier.models import Supplier

##############################################################################################
############################ SETORES E DIRETORIAS ############################################
##############################################################################################


class AbsctractDirectionSector(models.Model):
    """
    Classe abstrata base para Diretorias e Setores.
    
    Define campos comuns compartilhados entre Direction e Sector:
    - name: Nome da diretoria/setor
    - slug: Identificador único para URLs
    - accountable: Responsável pela diretoria/setor
    - address: Endereço físico
    
    Attributes:
        name (str): Nome da diretoria ou setor
        slug (str): Slug único gerado automaticamente a partir do nome
        accountable (str): Nome do responsável
        address (str): Endereço físico da diretoria/setor
    """
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
    """
    Representa uma Diretoria da Prefeitura.
    
    Herda campos de AbsctractDirectionSector (name, slug, accountable, address).
    Uma Diretoria pode conter múltiplos Setores.
    
    Example:
        >>> direction = Direction.objects.create(
        ...     name="Diretoria de TI",
        ...     accountable="João Silva",
        ...     address="Rua Principal, 123"
        ... )
    """
    class Meta:
        ordering = ("name",)
        verbose_name = "diretoria"
        verbose_name_plural = "diretorias"

    def get_absolute_url(self):
        return r("dashboard:diretoria", kwargs={"slug": self.slug})


class Sector(AbsctractDirectionSector):
    """
    Representa um Setor dentro de uma Diretoria.
    
    Herda campos de AbsctractDirectionSector (name, slug, accountable, address).
    Cada Setor pertence a uma Diretoria específica.
    
    Attributes:
        direction (Direction): Diretoria à qual este setor pertence
    """
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
        return r("dashboard:setor", kwargs={"slug": self.slug})


##############################################################################################
########################### LICITAÇÃO E SUPRIMENTOS ##########################################
##############################################################################################
STATUS_CHOICES = (("1", "Ativo"), ("2", "Inativo"))


class AbsBiddingMaterial(models.Model):
    """
    Classe abstrata base para Materiais e Licitações.
    
    Define campos comuns:
    - name: Nome do material/licitação
    - slug: Identificador único para URLs (gerado automaticamente)
    - supplier: Fornecedor associado
    
    NOTA: O campo 'status' foi removido deste modelo abstrato.
    Agora o status é gerenciado na tabela intermediária MaterialBidding,
    permitindo que um material tenha status diferentes em cada licitação.
    
    O slug é gerado automaticamente no método save() se não fornecido.
    """
    name = models.CharField("nome", max_length=200, blank=True)
    slug = models.SlugField("slug")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Bidding(AbsBiddingMaterial):
    """
    Representa uma licitação/pregão.
    
    O status da licitação é propagado automaticamente para todos os
    materiais vinculados via MaterialBidding quando alterado.
    """
    STATUS_CHOICES = (
        ("1", "Ativo"),
        ("2", "Inativo"),
    )
    
    date = models.DateField("data", blank=True, null=True)
    status = models.CharField(
        "status",
        max_length=1,
        choices=STATUS_CHOICES,
        default="1",
        help_text="Status da licitação (propagado para materiais vinculados)"
    )

    class Meta:
        ordering = ("date", "name")
        verbose_name = "licitação"
        verbose_name_plural = "licitações"

    def get_absolute_url(self):
        return r("dashboard:licitacao", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_base = slugify(self.name)
            original_slug = slug_base
            counter = 1
            while Bidding.objects.filter(slug=slug_base).exclude(pk=self.pk).exists():
                slug_base = f"{original_slug}-{counter}"
                counter += 1
            
            self.slug = slug_base
        
        # Detectar mudança de status
        status_changed = False
        if self.pk:
            try:
                old_instance = Bidding.objects.get(pk=self.pk)
                status_changed = old_instance.status != self.status
            except Bidding.DoesNotExist:
                pass
        
        result = super().save(*args, **kwargs)
        
        # Propagar mudança de status para MaterialBidding associados
        if status_changed:
            self.material_associations.update(status=self.status)
        
        return result


class Material(AbsBiddingMaterial):
    """
    Representa um material/suprimento que pode ser usado em múltiplas licitações.
    
    A relação com Bidding é Many-to-Many através da tabela intermediária MaterialBidding.
    """
    # Many-to-Many com Bidding através de MaterialBidding
    biddings = models.ManyToManyField(
        Bidding,
        through='MaterialBidding',
        related_name='materials',
        verbose_name='licitações',
        blank=True
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "material"
        verbose_name_plural = "materiais"

    def get_absolute_url(self):
        return r("dashboard:material", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            # Slug baseado apenas no nome
            slug_base = slugify(self.name)[:50]
            
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
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        verbose_name='fornecedor',
        related_name='bidding_materials',
        blank=True,
        null=True
    )
    price = models.DecimalField(
        "preço",
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Preço do material nesta licitação"
    )
    readjustment = models.FloatField(
        "reajuste (%)",
        default=0,
        help_text="Percentual de reajuste aplicado"
    )
    # price_snapshot mantido por compatibilidade temporária, será removido futuramente
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

    def total_price(self):
        """Retorna o preço total com reajuste aplicado."""
        if not self.price:
            return Decimal("0.00")
        
        if self.readjustment and self.readjustment != 0:
            total = float(self.price) + (float(self.price) * (self.readjustment / 100))
            return Decimal(str(total)).quantize(Decimal("0.00"))
        
        return self.price
    
    class Meta:
        ordering = ("bidding", "material")
        verbose_name = "material da licitação"
        verbose_name_plural = "materiais das licitações"
        unique_together = [['material', 'bidding']]
    
    def __str__(self):
        return f"{self.material.name} - {self.bidding.name}"
    
    def save(self, *args, **kwargs):
        # Captura price_snapshot automaticamente se não fornecido
        if not self.price_snapshot:
            self.price_snapshot = self.total_price()
        return super().save(*args, **kwargs)
