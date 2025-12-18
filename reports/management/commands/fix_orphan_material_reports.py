"""
Corrige MaterialReports órfãos (sem material_bidding) vinculando ao MaterialBidding correto
baseado no preço unitário.

Este script é executado UMA VEZ durante o deploy para corrigir dados inconsistentes.
"""
from django.core.management.base import BaseCommand
from reports.models import MaterialReport
from bidding_procurement.models import MaterialBidding
from decimal import Decimal


class Command(BaseCommand):
    help = 'Corrige MaterialReports órfãos vinculando ao MaterialBidding correto pelo preço.'

    # Mapeamento de preço -> MaterialBidding ID
    PRICE_TO_MATERIAL_BIDDING = {
        Decimal('129.00'): 155,  # BATERIA PARA NOBREAK 12V-7AH
        Decimal('8.00'): 75,      # MOUSE PAD
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a execução sem alterar o banco de dados',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # MaterialReports sem material_bidding
        orphans = MaterialReport.objects.filter(material_bidding__isnull=True)
        total = orphans.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nenhum MaterialReport órfão encontrado.'))
            return
        
        self.stdout.write(f'Encontrados {total} MaterialReport(s) órfão(s).')
        
        fixed_count = 0
        not_fixed = []
        
        for mr in orphans:
            price = mr.unitary_price
            report_num = mr.report.number_report if mr.report else 'SEM_LAUDO'
            
            if price in self.PRICE_TO_MATERIAL_BIDDING:
                mb_id = self.PRICE_TO_MATERIAL_BIDDING[price]
                
                try:
                    mb = MaterialBidding.objects.get(id=mb_id)
                    
                    if dry_run:
                        self.stdout.write(self.style.WARNING(
                            f'[DRY-RUN] Vincularia MR#{mr.id} (Laudo {report_num}) -> '
                            f'MB#{mb_id} ({mb.material.name})'
                        ))
                    else:
                        mr.material_bidding = mb
                        mr.save(update_fields=['material_bidding'])
                        self.stdout.write(self.style.SUCCESS(
                            f'Corrigido: MR#{mr.id} (Laudo {report_num}) -> '
                            f'MB#{mb_id} ({mb.material.name})'
                        ))
                    fixed_count += 1
                    
                except MaterialBidding.DoesNotExist:
                    not_fixed.append((mr.id, report_num, price, f'MB#{mb_id} não existe'))
            else:
                not_fixed.append((mr.id, report_num, price, 'Preço não mapeado'))
        
        # Resumo
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f'Simulação concluída. {fixed_count} seriam corrigidos.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Concluído. {fixed_count} MaterialReport(s) corrigido(s).'
            ))
        
        if not_fixed:
            self.stdout.write(self.style.WARNING(f'\n{len(not_fixed)} não corrigido(s):'))
            for mr_id, report_num, price, reason in not_fixed:
                self.stdout.write(f'  MR#{mr_id} (Laudo {report_num}) R${price} - {reason}')
