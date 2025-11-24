from django.db import migrations
from django.utils.text import slugify

def fix_slugs_robust(apps, schema_editor):
    Material = apps.get_model('dashboard', 'Material')
    Bidding = apps.get_model('dashboard', 'Bidding')
    Direction = apps.get_model('dashboard', 'Direction')
    Sector = apps.get_model('dashboard', 'Sector')

    for Model in [Material, Bidding, Direction, Sector]:
        for obj in Model.objects.all():
            if not obj.slug or obj.slug.strip() == "":
                # Tenta gerar pelo nome
                new_slug = slugify(obj.name)
                
                # Se ainda vazio (nome vazio ou caracteres especiais), usa fallback
                if not new_slug:
                    model_name = Model.__name__.lower()
                    new_slug = f"{model_name}-{obj.id}"
                
                obj.slug = new_slug
                obj.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0015_auto_20251124_1343'),
    ]

    operations = [
        migrations.RunPython(fix_slugs_robust),
    ]
