from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from organizational_structure.models import Direction, Sector


@receiver(pre_save, sender=Direction)
def generate_direction_slug(sender, instance, **kwargs):
    if not instance.slug:
        slug_base = slugify(instance.name)
        original_slug = slug_base
        counter = 1
        while Direction.objects.filter(slug=slug_base).exclude(pk=instance.pk).exists():
            slug_base = f"{original_slug}-{counter}"
            counter += 1
        instance.slug = slug_base


@receiver(pre_save, sender=Sector)
def generate_sector_slug(sender, instance, **kwargs):
    if not instance.slug:
        slug_base = slugify(instance.name)
        original_slug = slug_base
        counter = 1
        while Sector.objects.filter(slug=slug_base).exclude(pk=instance.pk).exists():
            slug_base = f"{original_slug}-{counter}"
            counter += 1
        instance.slug = slug_base
