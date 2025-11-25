from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bidding_supplier', '0001_initial'),
        ('dashboard', '0017_bidding_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='materialbidding',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Preço do material nesta licitação', max_digits=8, null=True, verbose_name='preço'),
        ),
        migrations.AddField(
            model_name='materialbidding',
            name='readjustment',
            field=models.FloatField(default=0, help_text='Percentual de reajuste aplicado', verbose_name='reajuste (%)'),
        ),
        migrations.AddField(
            model_name='materialbidding',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bidding_materials', to='bidding_supplier.supplier', verbose_name='fornecedor'),
        ),
    ]
