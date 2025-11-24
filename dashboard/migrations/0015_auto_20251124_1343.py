from django.db import migrations
from django.utils.text import slugify

def fix_slugs(apps, schema_editor):
    Material = apps.get_model('dashboard', 'Material')
    Bidding = apps.get_model('dashboard', 'Bidding')
    Direction = apps.get_model('dashboard', 'Direction')
    Sector = apps.get_model('dashboard', 'Sector')

    for Model in [Material, Bidding, Direction, Sector]:
        for obj in Model.objects.all():
            if not obj.slug:
                obj.slug = slugify(obj.name)
                obj.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_alter_direction_accountable_alter_direction_address_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_slugs),
    ]
