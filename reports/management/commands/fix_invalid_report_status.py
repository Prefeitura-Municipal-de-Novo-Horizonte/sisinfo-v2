"""
Corrige laudos com status incorreto ('2') para status válido ('3' = Finalizado).
Este script é executado uma vez para limpar dados inconsistentes.
"""
from django.core.management.base import BaseCommand
from reports.models import Report


class Command(BaseCommand):
    help = 'Corrige laudos com status inválido (2) para status válido (3 = Finalizado).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a execução sem alterar o banco de dados',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Laudos com status inválido
        invalid_reports = Report.objects.filter(status='2')
        total = invalid_reports.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nenhum laudo com status inválido encontrado.'))
            return
        
        self.stdout.write(f'Encontrados {total} laudo(s) com status inválido (2).')
        
        for report in invalid_reports:
            msg = f'Laudo #{report.pk} ({report.number_report}) - Setor: {report.sector}'
            
            if dry_run:
                self.stdout.write(self.style.WARNING(f'[DRY-RUN] Corrigiria: {msg}'))
            else:
                report.status = '3'  # Finalizado
                report.save(update_fields=['status'])
                self.stdout.write(self.style.SUCCESS(f'Corrigido: {msg}'))
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS('Simulação concluída. Nenhuma alteração feita.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Concluído. {total} laudo(s) corrigido(s).'))
