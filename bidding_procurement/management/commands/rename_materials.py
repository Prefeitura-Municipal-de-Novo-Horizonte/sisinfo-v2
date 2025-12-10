"""
Comando para renomear materiais usando coluna 'equivale á' do CSV.

Se a coluna tiver valor, renomeia o material.
Se estiver vazia, mantém o nome atual.
"""
import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from bidding_procurement.models import Material


class Command(BaseCommand):
    help = 'Renomeia materiais usando coluna equivale á do CSV'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str, default='relatorio_materiais_detalhado.csv')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        csv_file = options['csv']
        dry_run = options['dry_run']

        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('RENOMEANDO MATERIAIS'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY-RUN MODE]\n'))

        # Ler CSV
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        renamed = 0

        with transaction.atomic():
            for row in rows:
                material_id = row['id']
                nome_atual = row['nome']
                nome_correto = (row.get('equivale á') or '').strip()

                # Se tem nome correto na coluna, renomear
                if nome_correto and nome_correto != nome_atual:
                    material = Material.objects.filter(id=material_id).first()
                    
                    if material:
                        self.stdout.write(f'\n📝 ID {material_id}:')
                        self.stdout.write(f'  De: "{material.name}"')
                        self.stdout.write(f'  Para: "{nome_correto}"')
                        
                        if not dry_run:
                            material.name = nome_correto.upper()  # Maiúsculo
                            material.save()
                            self.stdout.write(self.style.SUCCESS('  ✓ Renomeado!'))
                            renamed += 1
                        else:
                            self.stdout.write('  [DRY-RUN] Seria renomeado')
                            renamed += 1

        # Resumo
        self.stdout.write('\n' + '='*80)
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\n[DRY-RUN] {renamed} materiais seriam renomeados\n'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ {renamed} materiais renomeados!\n'
            ))
        self.stdout.write('='*80 + '\n')
