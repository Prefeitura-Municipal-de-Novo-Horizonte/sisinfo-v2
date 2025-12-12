from decimal import Decimal

from django.db import models
from django.shortcuts import reverse as r
from django.template.defaultfilters import slugify

from bidding_supplier.models import Supplier

STATUS_CHOICES = (("1", "Ativo"), ("2", "Inativo"))


class AbsBiddingMaterial(models.Model):
    """
    Classe abstrata base para Materiais e Licitações.
    
    Define campos comuns:
    - name: Nome do material/licitação
    - slug: Identificador único para URLs (gerado automaticamente)
    - supplier: Fornecedor associado (removido nesta versão, mantido em MaterialBidding)
    
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
    
    # Novos campos para importação automatizada
    administrative_process = models.CharField(
        "processo administrativo",
        max_length=20,
        blank=True,
        help_text="Ex: 121/25"
    )
    modality = models.CharField(
        "modalidade",
        max_length=100,
        blank=True,
        help_text="Ex: PREGÃO ELETRÔNICO"
    )
    modality_number = models.IntegerField(
        "número da modalidade",
        null=True,
        blank=True,
        help_text="Ex: 38"
    )
    validity_date = models.DateField(
        "prazo de validade",
        null=True,
        blank=True
    )
    object_description = models.TextField(
        "objeto/descrição",
        blank=True
    )

    class Meta:
        ordering = ("date", "name")
        verbose_name = "licitação"
        verbose_name_plural = "licitações"
        db_table = "dashboard_bidding"

    def get_absolute_url(self):
        """Retorna a URL absoluta para os detalhes da licitação."""
        if not self.slug:
            return "#"  # Retorna # se slug estiver vazio
        return r("bidding_procurement:licitacao", kwargs={"slug": self.slug})
    
    def get_active_materials(self):
        """
        Retorna apenas materiais ativos vinculados a esta licitação.
        
        Returns:
            QuerySet: MaterialBidding com status ativo ('1')
        """
        return self.material_associations.filter(status='1').select_related('material', 'supplier')
    
    def get_inactive_materials(self):
        """
        Retorna apenas materiais inativos vinculados a esta licitação.
        
        Returns:
            QuerySet: MaterialBidding com status inativo ('2')
        """
        return self.material_associations.filter(status='2').select_related('material', 'supplier')




class Material(AbsBiddingMaterial):
    """
    Representa um material/suprimento que pode ser usado em múltiplas licitações.
    
    A relação com Bidding é Many-to-Many através da tabela intermediária MaterialBidding.
    """
    # Campos adicionais
    brand = models.CharField(
        "marca",
        max_length=200,
        blank=True,
        help_text="Marca do material (ex: TSA AD-09, DEKO 764-J CAT6)"
    )
    unit = models.CharField(
        "unidade",
        max_length=20,
        blank=True,
        help_text="Unidade de medida (ex: un, M, pc, cx)"
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
        ordering = ("name",)
        verbose_name = "material"
        verbose_name_plural = "materiais"
        db_table = "dashboard_material"

    def get_absolute_url(self):
        """Retorna a URL absoluta para os detalhes do material."""
        return r("bidding_procurement:material", kwargs={"slug": self.slug})




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
        help_text="Status do material nesta licitação específica"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='material_biddings',
        verbose_name='fornecedor vencedor',
        help_text="Fornecedor que venceu este item na licitação"
    )
    quantity = models.IntegerField(
        "quantidade licitada",
        default=0,
        help_text="Quantidade total licitada deste material"
    )
    price = models.DecimalField(
        "preço",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Preço do material nesta licitação"
    )
    readjustment = models.DecimalField(
        "reajuste",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
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

    def get_available_quantity(self):
        """
        Calcula quantidade disponível (licitada - usada em laudos).
        
        Returns:
            int: Quantidade disponível para uso
        """
        from reports.models import MaterialReport
        from django.db.models import Sum
        
        used = MaterialReport.objects.filter(
            material_bidding=self
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        return self.quantity - used

    def total_price(self):
        """
        Calcula o preço total considerando o reajuste.
        
        Returns:
            Decimal: Preço final com reajuste aplicado.
        """
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
        db_table = "dashboard_materialbidding"
    
    def __str__(self):
        return f"{self.material.name} - {self.bidding.name}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para capturar o snapshot do preço.
        """
        # Captura price_snapshot automaticamente se não fornecido
        if not self.price_snapshot:
            self.price_snapshot = self.total_price()
        return super().save(*args, **kwargs)
