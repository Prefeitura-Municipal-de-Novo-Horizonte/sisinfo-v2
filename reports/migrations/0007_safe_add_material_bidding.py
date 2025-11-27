# Generated manually - Safe migration for production

from django.db import migrations, models, connection
import django.db.models.deletion


def check_column_exists(table_name, column_name):
    """Verifica se uma coluna existe na tabela."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name=%s AND column_name=%s
        """, [table_name, column_name])
        return cursor.fetchone() is not None


def migrate_material_to_material_bidding(apps, schema_editor):
    """
    Migra dados de MaterialReport.material para MaterialReport.material_bidding.
    Apenas se o campo material_bidding existir e material ainda existir.
    """
    # Verificar se as colunas existem
    has_material = check_column_exists('reports_materialreport', 'material_id')
    has_material_bidding = check_column_exists('reports_materialreport', 'material_bidding_id')
    
    if not has_material_bidding:
        print("Campo material_bidding não existe ainda, pulando migração de dados...")
        return
    
    if not has_material:
        print("Campo material já foi removido, pulando migração de dados...")
        return
    
    MaterialReport = apps.get_model('reports', 'MaterialReport')
    Material = apps.get_model('bidding_procurement', 'Material')
    Bidding = apps.get_model('bidding_procurement', 'Bidding')
    MaterialBidding = apps.get_model('bidding_procurement', 'MaterialBidding')
    
    from datetime import date
    
    # Criar ou obter licitação legado
    legacy_bidding, _ = Bidding.objects.get_or_create(
        name="Licitação Legado - Migração",
        defaults={
            'date': date.today(),
            'status': '1',
        }
    )
    
    # Migrar cada MaterialReport que tem material mas não tem material_bidding
    count = 0
    for material_report in MaterialReport.objects.filter(material_bidding__isnull=True):
        if material_report.material_id:
            try:
                material = Material.objects.get(pk=material_report.material_id)
                
                # Procurar ou criar MaterialBidding
                material_bidding = MaterialBidding.objects.filter(material=material).first()
                
                if not material_bidding:
                    material_bidding = MaterialBidding.objects.create(
                        material=material,
                        bidding=legacy_bidding,
                        status='1',
                        price=material_report.unitary_price if material_report.unitary_price else 0,
                        readjustment=0
                    )
                
                material_report.material_bidding = material_bidding
                material_report.save()
                count += 1
            except Material.DoesNotExist:
                pass
    
    print(f"Migrados {count} MaterialReports")


class Migration(migrations.Migration):

    dependencies = [
        ('bidding_procurement', '0001_initial'),
        ('reports', '0006_alter_materialreport_material'),
    ]

    operations = [
        # Adicionar campos apenas se não existirem (RunPython customizado)
        migrations.RunPython(
            code=lambda apps, schema_editor: None if check_column_exists('reports_invoice', 'file') else 
                migrations.AddField(
                    model_name='invoice',
                    name='file',
                    field=models.FileField(blank=True, null=True, upload_to='invoices/%Y/%m/', verbose_name='arquivo da nota'),
                ).database_forwards('reports', schema_editor, None, None),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: None if check_column_exists('reports_invoice', 'xml_content') else 
                migrations.AddField(
                    model_name='invoice',
                    name='xml_content',
                    field=models.TextField(blank=True, null=True, verbose_name='conteúdo XML'),
                ).database_forwards('reports', schema_editor, None, None),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: None if check_column_exists('reports_materialreport', 'material_bidding_id') else 
                migrations.AddField(
                    model_name='materialreport',
                    name='material_bidding',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='materiais_laudos', to='bidding_procurement.materialbidding', verbose_name='material da licitação'),
                ).database_forwards('reports', schema_editor, None, None),
            reverse_code=migrations.RunPython.noop,
        ),
        # Migrar dados
        migrations.RunPython(migrate_material_to_material_bidding, reverse_code=migrations.RunPython.noop),
        # Remover campo antigo apenas se ainda existir
        migrations.RunPython(
            code=lambda apps, schema_editor: 
                migrations.RemoveField(
                    model_name='materialreport',
                    name='material',
                ).database_forwards('reports', schema_editor, None, None) if check_column_exists('reports_materialreport', 'material_id') else None,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
