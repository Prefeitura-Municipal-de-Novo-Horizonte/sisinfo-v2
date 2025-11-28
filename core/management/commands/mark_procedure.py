from django.core.management.base import BaseCommand
from core.models import DeploymentProcedure


class Command(BaseCommand):
    help = 'Marca um procedimento de deploy como executado'

    def add_arguments(self, parser):
        parser.add_argument('procedure_name', type=str, help='Nome do procedimento')
        parser.add_argument(
            '--notes',
            type=str,
            default='',
            help='Notas sobre a execução'
        )
        parser.add_argument(
            '--failed',
            action='store_true',
            help='Marcar como falha'
        )

    def handle(self, *args, **options):
        procedure_name = options['procedure_name']
        notes = options['notes']
        success = not options['failed']
        
        procedure, created = DeploymentProcedure.objects.get_or_create(
            name=procedure_name,
            defaults={
                'success': success,
                'notes': notes
            }
        )
        
        if not created:
            procedure.success = success
            procedure.notes = notes
            procedure.save()
            self.stdout.write(self.style.WARNING(f'⚠ Procedimento "{procedure_name}" atualizado'))
        else:
            status = "✓" if success else "✗"
            self.stdout.write(self.style.SUCCESS(f'{status} Procedimento "{procedure_name}" marcado como executado'))
