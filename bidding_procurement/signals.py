from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from bidding_procurement.models import Bidding, Material


@receiver(pre_save, sender=Bidding)
def generate_bidding_slug(sender, instance, **kwargs):
    if not instance.slug:
        slug_base = slugify(instance.name)
        original_slug = slug_base
        counter = 1
        while Bidding.objects.filter(slug=slug_base).exclude(pk=instance.pk).exists():
            slug_base = f"{original_slug}-{counter}"
            counter += 1
        instance.slug = slug_base


@receiver(pre_save, sender=Material)
def generate_material_slug(sender, instance, **kwargs):
    if not instance.slug:
        slug_base = slugify(instance.name)[:50]
        original_slug = slug_base
        counter = 1
        while Material.objects.filter(slug=slug_base).exclude(pk=instance.pk).exists():
            slug_base = f"{original_slug}-{counter}"
            counter += 1
        instance.slug = slug_base


@receiver(post_save, sender=Bidding)
def propagate_bidding_status(sender, instance, created, **kwargs):
    """
    Propaga o status da licitação para todos os materiais vinculados.
    
    Caso de uso: Quando uma licitação é desativada, todos os materiais
    vinculados devem ser desativados automaticamente para não aparecerem
    em listagens de materiais ativos.
    
    Args:
        sender: Classe do modelo (Bidding)
        instance: Instância da licitação sendo salva
        created: True se é uma nova instância, False se é atualização
        **kwargs: Argumentos adicionais do signal
    """
    if not created:
        # Atualiza status de todos os MaterialBidding associados
        # para corresponder ao status da licitação
        instance.material_associations.update(status=instance.status)
