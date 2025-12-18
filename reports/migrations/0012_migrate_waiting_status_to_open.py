from django.db import migrations

def migrate_status(apps, schema_editor):
    Report = apps.get_model('reports', 'Report')
    # Status 2 (Aguardando) -> 1 (Aberto)
    count = Report.objects.filter(status='2').update(status='1')
    print(f"\nMigrados {count} laudos de 'Aguardando' para 'Aberto'.")

class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0011_remove_deliverynote_commitment_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_status),
    ]
