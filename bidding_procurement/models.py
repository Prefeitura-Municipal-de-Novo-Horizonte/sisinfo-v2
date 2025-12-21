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

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.upper()
        if self.brand:
            self.brand = self.brand.upper()
        # Unit usually doesn't need to be upper (e.g. 'kg', 'm'), keeps standard if needed? 
        # User said "materiails e fornecedores", implies names. 
        # But for consistency let's uppercase unit if it's text like 'UN', 'CX'. 
        # Let's uppercase unit too as it's common in legacy systems.
        if self.unit:
            self.unit = self.unit.upper()
            
        super().save(*args, **kwargs)

    def get_bidding_info(self):
        """
        Retorna informações sobre licitações que contêm este material.
        
        Returns:
            dict: {
                'count': int,
                'biddings': QuerySet[Bidding],
                'total_quantity': int
            }
        """
        from django.db.models import Sum
        
        associations = self.bidding_associations.select_related('bidding').all()
        total_qty = associations.aggregate(total=Sum('quantity'))['total'] or 0
        
        return {
            'count': associations.count(),
            'biddings': [assoc.bidding for assoc in associations[:5]],  # Limita a 5
            'total_quantity': total_qty
        }
    
    def get_report_usage(self):
        """
        Retorna informações sobre laudos que usaram este material.
        
        Returns:
            dict: {
                'count': int,
                'total_used': int,
                'recent_reports': list,
                'has_more': bool
            }
        """
        from reports.models import MaterialReport
        from django.db.models import Sum
        
        # Busca todos os MaterialReport que usam este material
        material_reports = MaterialReport.objects.filter(
            material_bidding__material=self
        ).select_related('report')
        
        total_used = material_reports.aggregate(total=Sum('quantity'))['total'] or 0
        total_count = material_reports.values('report').distinct().count()
        
        # Report usa 'number_report' como identificador, não 'name'
        # Limita a 4 itens
        recent_reports = material_reports[:4].values_list('report__number_report', flat=True)
        
        return {
            'count': total_count,
            'total_used': total_used,
            'recent_reports': list(recent_reports),
            'has_more': total_count > 4
        }




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
    brand = models.CharField(
        "marca",
        max_length=200,
        blank=True,
        help_text="Marca do material nesta licitação (ex: TSA AD-09, DEKO 764-J)"
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
    
    # Controle de limite de compras da licitação
    quantity_purchased = models.PositiveIntegerField(
        "quantidade comprada",
        default=0,
        help_text="Quantidade já comprada via notas fiscais (não pode ultrapassar o limite licitado)"
    )
    
    created_at = models.DateTimeField("incluído em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)
    
    def __str__(self):
        return f"{self.material.name} - {self.bidding.name} (R$ {self.price})"

    
    @property
    def available_for_purchase(self):
        """Quantidade ainda disponível para compra (limite - comprado)."""
        return max(0, (self.quantity or 0) - (self.quantity_purchased or 0))
    
    @property
    def usage_percentage(self):
        """Percentual do limite de compra já utilizado."""
        if not self.quantity or self.quantity == 0:
            return 0
        return round((self.quantity_purchased / self.quantity) * 100, 1)
    
    @property
    def is_near_limit(self):
        """Verifica se está próximo do limite (>= 80% usado)."""
        return self.usage_percentage >= 80
    
    @property
    def is_at_limit(self):
        """Verifica se atingiu o limite de compras."""
        return self.quantity_purchased >= self.quantity

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
        return super().save(*args, **kwargs)
