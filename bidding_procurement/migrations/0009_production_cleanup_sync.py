from django.db import migrations
from django.core.management import call_command
import logging

def run_sync_scripts(apps, schema_editor):
    logger = logging.getLogger(__name__)
    logger.info("🛠️  Iniciando Migração de Dados: Sincronização e Correção de Produção")
    
    try:
        # 1. Corrigir nomes de materiais (Typos, Case, Merge)
        logger.info("1/3 Executando fix_material_names...")
        call_command('fix_material_names')
        
        # 2. Atualizar fornecedores
        logger.info("2/3 Executando update_supplier_cnpjs...")
        call_command('update_supplier_cnpjs')
        
        # 3. Sincronizar licitações (Strict Mode)
        logger.info("3/3 Executando sync_bidding_materials...")
        call_command('sync_bidding_materials')
        
        logger.info("✅ Migração de Dados Concluída com Sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Falha na Migração de Dados: {str(e)}")
        # Não damos raise para não quebrar o deploy, mas logamos o erro crítico.
        # Em migrations de dados complexas, às vezes é melhor falhar parcialmente 
        # e permitir correção manual do que bloquear o startup do app.
        raise e

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
