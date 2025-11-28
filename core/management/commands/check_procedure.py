from django.core.management.base import BaseCommand
from core.models import DeploymentProcedure
import sys


class Command(BaseCommand):
    help = 'Verifica se um procedimento de deploy já foi executado'

    def add_arguments(self, parser):
        parser.add_argument('procedure_name', type=str, help='Nome do procedimento')

    def handle(self, *args, **options):
        procedure_name = options['procedure_name']
        
        exists = DeploymentProcedure.objects.filter(
            name=procedure_name,
            success=True
        ).exists()
        
        if exists:
            self.stdout.write(self.style.SUCCESS(f'✓ Procedimento "{procedure_name}" já foi executado'))
            sys.exit(0)  # Exit code 0 = já executado
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Procedimento "{procedure_name}" ainda não foi executado'))
            sys.exit(1)  # Exit code 1 = não executado
