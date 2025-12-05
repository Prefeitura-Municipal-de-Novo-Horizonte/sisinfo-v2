# Fixed migration to standard Django format

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bidding_procurement', '0003_materialbidding_quantity'),
        ('reports', '0007_safe_add_material_bidding'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='materialreport',
            name='material',
        ),
    ]
