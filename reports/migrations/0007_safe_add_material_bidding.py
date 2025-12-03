# Fixed migration to standard Django format with data migration

from django.db import migrations, models
import django.db.models.deletion

def migrate_legacy_data(apps, schema_editor):
    try:
        MaterialReport = apps.get_model('reports', 'MaterialReport')
        Material = apps.get_model('bidding_procurement', 'Material')
        Bidding = apps.get_model('bidding_procurement', 'Bidding')
        MaterialBidding = apps.get_model('bidding_procurement', 'MaterialBidding')
        from datetime import date

        legacy_bidding, _ = Bidding.objects.get_or_create(
            name="Licitação Legado - Migração",
            defaults={'date': date.today(), 'status': '1'}
        )

        for item in MaterialReport.objects.filter(material_bidding__isnull=True):
            if item.material_id:
                try:
                    mat = Material.objects.get(pk=item.material_id)
                    mb, _ = MaterialBidding.objects.get_or_create(
                        material=mat,
                        bidding=legacy_bidding,
                        defaults={'status': '1', 'price': item.unitary_price or 0}
                    )
                    item.material_bidding = mb
                    item.save()
                except Material.DoesNotExist:
                    pass
    except Exception as e:
        print(f"Skipping data migration due to error: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ('bidding_procurement', '0001_initial'),
        ('reports', '0006_alter_materialreport_material'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='invoices/%Y/%m/', verbose_name='arquivo da nota'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='xml_content',
            field=models.TextField(blank=True, null=True, verbose_name='conteúdo XML'),
        ),
        migrations.AddField(
            model_name='materialreport',
            name='material_bidding',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='materiais_laudos', to='bidding_procurement.materialbidding', verbose_name='material da licitação'),
        ),
        migrations.RunPython(migrate_legacy_data, migrations.RunPython.noop),
    ]
