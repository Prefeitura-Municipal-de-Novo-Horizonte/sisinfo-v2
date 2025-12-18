from django.core.management.base import BaseCommand
from reports.models import Report
from bidding_procurement.models import Bidding

class Command(BaseCommand):
    help = 'Fecha laudos abertos que possuem materiais de licitações inativas.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a execução sem alterar o banco de dados',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Reports abertos (1) ou aguardando (2)
        # Que possuem materiais vinculados a uma Licitação com status '2' (Inativo)
        stale_reports = Report.objects.filter(
            status__in=['1', '2'],
            materiais__material_bidding__bidding__status='2'
        ).distinct()

        total = stale_reports.count()
        self.stdout.write(f"Encontrados {total} laudos com materiais de licitações inativas.")

        for report in stale_reports:
            msg = f"Laudo #{report.pk} ({report.number_report}) - Setor: {report.sector}"
            
            # Listar licitações inativas envolvidas
            inactive_biddings = Bidding.objects.filter(
                material_associations__materiais_laudos__report=report,
                status='2'
            ).distinct().values_list('name', flat=True)
            
            biddings_str = ", ".join(inactive_biddings)
            
            if dry_run:
                self.stdout.write(self.style.WARNING(f"[DRY-RUN] Fecharia: {msg} (Licitações: {biddings_str})"))
            else:
                report.status = '3' # Finalizado
                # Adiciona observação automática se houver campo apropriado ou apenas fecha
                # Como justification é obrigatório e já deve ter algo, vamos concatenar uma nota system
                report.justification += f"\n\n[SISTEMA] Fechado automaticamente em razão de licitação inativa ({biddings_str})."
                report.save()
                self.stdout.write(self.style.SUCCESS(f"Fechado: {msg}"))

        if dry_run:
            self.stdout.write(self.style.SUCCESS('Simulação concluída. Nenhuma alteração feita.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Concluído. {total} laudos foram fechados.'))
