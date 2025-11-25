from django.db import migrations

def migrate_data(apps, schema_editor):
    MaterialBidding = apps.get_model('dashboard', 'MaterialBidding')
    Material = apps.get_model('dashboard', 'Material')
    
    for mb in MaterialBidding.objects.all():
        # Copy data from related Material
        # Note: We access the material via the foreign key
        # Since we haven't removed the fields from Material yet, they are accessible
        material = mb.material
        mb.supplier = material.supplier
        mb.price = material.price
        mb.readjustment = material.readjustment
        mb.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0018_add_fields_to_material_bidding'),
    ]

    operations = [
        migrations.RunPython(migrate_data),
    ]
