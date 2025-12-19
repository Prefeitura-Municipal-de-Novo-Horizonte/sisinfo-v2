from django.db import migrations


def migrate_data(apps, schema_editor):
    """
    Migra dados de Material para MaterialBidding.
    Usa SQL raw para evitar problemas de schema quando colunas ainda não existem.
    """
    # Em banco novo, não há dados para migrar
    # Esta migração era para bancos existentes antes da reestruturação
    cursor = schema_editor.connection.cursor()
    
    # Verificar se há dados para migrar
    cursor.execute("SELECT COUNT(*) FROM dashboard_materialbidding")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("  Nenhum dado para migrar (banco novo)")
        return
    
    # Migrar usando SQL raw (somente colunas que existem nesta fase)
    cursor.execute("""
        UPDATE dashboard_materialbidding mb
        SET supplier_id = m.supplier_id,
            price = m.price,
            readjustment = m.readjustment
        FROM dashboard_material m
        WHERE mb.material_id = m.id
          AND (mb.supplier_id IS NULL OR mb.price IS NULL)
    """)
    print(f"  Dados migrados: {cursor.rowcount} registros")


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0018_add_fields_to_material_bidding'),
    ]

    operations = [
        migrations.RunPython(migrate_data, migrations.RunPython.noop),
    ]

