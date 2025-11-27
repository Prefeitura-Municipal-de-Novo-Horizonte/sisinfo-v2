# Generated manually

from django.db import migrations, models
import django.db.models.deletion


def migrate_material_to_material_bidding(apps, schema_editor):
    """
    Migra dados de MaterialReport.material para MaterialReport.material_bidding.
    Cria MaterialBidding para materiais que não têm vinculo com licitação.
    """
    MaterialReport = apps.get_model('reports', 'MaterialReport')
    Material = apps.get_model('bidding_procurement', 'Material')
    Bidding = apps.get_model('bidding_procurement', 'Bidding')
    MaterialBidding = apps.get_model('bidding_procurement', 'MaterialBidding')
    Supplier = apps.get_model('bidding_supplier', 'Supplier')
    
    from datetime import date
    
    # Criar ou obter licitação legado
    legacy_bidding, _ = Bidding.objects.get_or_create(
        name="Licitação Legado - Migração",
        defaults={
            'date': date.today(),
            'status': '1',
        }
    )
    
    # Migrar cada MaterialReport
    for material_report in MaterialReport.objects.all():
        if material_report.material:
            # Tentar encontrar MaterialBidding existente para este material
            material_bidding = MaterialBidding.objects.filter(
                material=material_report.material
            ).first()
            
            # Se não existir, criar um novo vinculado à licitação legado
            if not material_bidding:
                material_bidding = MaterialBidding.objects.create(
                    material=material_report.material,
                    bidding=legacy_bidding,
                    status='1',
                    price=material_report.unitary_price if material_report.unitary_price else 0,
                    readjustment=0
                )
            
            # Atualizar o MaterialReport
            material_report.material_bidding = material_bidding
            material_report.save()


class Migration(migrations.Migration):

    dependencies = [
        ('bidding_procurement', '0001_initial'),
        ('bidding_supplier', '0001_initial'),
        ('reports', '0006_alter_materialreport_material'),
    ]

    operations = [
        # Adicionar campos novos primeiro
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
        # Migrar dados
        migrations.RunPython(migrate_material_to_material_bidding, reverse_code=migrations.RunPython.noop),
        # Remover campo antigo
        migrations.RemoveField(
            model_name='materialreport',
            name='material',
        ),
    ]
