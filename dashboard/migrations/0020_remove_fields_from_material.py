from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0019_migrate_material_data'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='material',
            options={'ordering': ('name',), 'verbose_name': 'material', 'verbose_name_plural': 'materiais'},
        ),
        migrations.RemoveField(
            model_name='material',
            name='price',
        ),
        migrations.RemoveField(
            model_name='material',
            name='readjustment',
        ),
        migrations.RemoveField(
            model_name='material',
            name='supplier',
        ),
    ]
