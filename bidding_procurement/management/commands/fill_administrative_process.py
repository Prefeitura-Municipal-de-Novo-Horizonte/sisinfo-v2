from django.core.management.base import BaseCommand
from bidding_procurement.models import Bidding
import re


class Command(BaseCommand):
    help = 'Preenche campo administrative_process das licitações antigas baseado no nome'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria feito sem executar'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.WARNING('\n=== PREENCHENDO PROCESSO ADMINISTRATIVO ===\n'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: Nenhuma alteração será feita\n'))
        
        # Buscar licitações sem processo administrativo
        biddings = Bidding.objects.filter(administrative_process__isnull=True) | \
                   Bidding.objects.filter(administrative_process='')
        
        updated = 0
        
        for bidding in biddings:
            # Extrair processo do nome
            # Formatos possíveis:
            # - "Processo Licitatório 121/25"
            # - "Processo Licitatório Nº 167/2024"
            
            match = re.search(r'(\d+)/(\d+)', bidding.name)
            if match:
                process_num = match.group(1)
                year = match.group(2)
                
                # Padronizar formato: XXX/YY
                if len(year) == 4:
                    year = year[-2:]  # Pegar últimos 2 dígitos
                
                administrative_process = f"{process_num}/{year}"
                
                self.stdout.write(f'{bidding.name}')
                self.stdout.write(f'  Processo: {administrative_process}')
                
                if not dry_run:
                    bidding.administrative_process = administrative_process
                    bidding.save()
                    self.stdout.write(self.style.SUCCESS('  ✓ Atualizado'))
                else:
                    self.stdout.write(self.style.WARNING('  [DRY-RUN] Seria atualizado'))
                
                updated += 1
            else:
                self.stdout.write(self.style.WARNING(f'{bidding.name}'))
                self.stdout.write('  ⚠ Não foi possível extrair processo do nome')
        
        if updated > 0:
            self.stdout.write(self.style.SUCCESS(f'\n✓ {updated} licitações atualizadas'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Nenhuma licitação precisa ser atualizada'))
