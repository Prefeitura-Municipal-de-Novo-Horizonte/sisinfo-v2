from django.db import migrations
import logging

def run_sync_scripts(apps, schema_editor):
    """
    NOTA: Esta migração foi desativada pois os management commands originais
    (fix_material_names, update_supplier_cnpjs, sync_bidding_materials) foram removidos.
    
    A migração agora é um no-op para permitir a aplicação normal das migrações.
    """
    logger = logging.getLogger(__name__)
    logger.info("⏭️  Migração 0009_production_cleanup_sync: Pulando (comandos não disponíveis)")

def reverse_func(apps, schema_editor):
    # Alterações de dados complexas são irreversíveis automaticamente.
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('bidding_procurement', '0008_add_brand_to_materialbidding'),
    ]

    operations = [
        migrations.RunPython(run_sync_scripts, reverse_func),
    ]
