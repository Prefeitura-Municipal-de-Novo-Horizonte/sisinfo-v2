from django.db import models
from django.shortcuts import resolve_url as r
from django.template.defaultfilters import slugify

# Create your models here.
##############################################################################################
############################ SETORES E DIRETORIAS ############################################
##############################################################################################

class AbsctactDirectionSector(models.Model):
    name = models.CharField('nome', max_length=200, blank=True, null=True)
    slug = models.SlugField('slug')
    accountable = models.CharField('responsavel', max_length=200, blank=True)

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
        ('DI', 'Diretoria'),
        ('SE', 'Secretária'),
        ('DE', 'Departamento'),
        ('GA', 'Gabinete')
        )
    kind = models.CharField('tipo', max_length=2, choices=KIND)
    
    class Meta:
        ordering = ['kind', 'name']
        verbose_name = 'diretoria'
        verbose_name_plural = 'diretorias'
    
    def get_absolute_url(self):
        return r('dashboard.diretoria', slug=self.slug)
    
    
class Sector(AbsctactDirectionSector):
    direction = models.ForeignKey('Direction', on_delete=models.DO_NOTHING, blank=True)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address = models.TextField()

    class Meta:
        ordering = ['direction', 'name']
        verbose_name ='setor'
        verbose_name_plural ='setores'
    
    def get_absolute_url(self):
        return r('dashboard.diretoria', slug=self.slug)
        
        