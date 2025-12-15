from django.db import models
from django.shortcuts import reverse as r
from django.template.defaultfilters import slugify


class AbsctactDirectionSector(models.Model):
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



class Direction(AbsctactDirectionSector):
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
        db_table = 'dashboard_direction'

    def get_absolute_url(self):
        return r("organizational_structure:diretoria", kwargs={"slug": self.slug})


class Sector(AbsctactDirectionSector):
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
        related_name="setores",
        blank=True,
        null=True,
    )
    phone = models.CharField("telefone", max_length=15, blank=True, null=True)
    email = models.EmailField("email", max_length=200, blank=True, null=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "setor"
        verbose_name_plural = "setores"
        db_table = 'dashboard_sector'

    def get_absolute_url(self):
        return r("organizational_structure:setor", kwargs={"slug": self.slug})
