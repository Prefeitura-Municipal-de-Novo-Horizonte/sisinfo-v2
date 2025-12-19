"""
Management command para restaurar dados do backup.
Pode ser chamado via URL protegida ou linha de comando.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from pathlib import Path


class Command(BaseCommand):
    help = 'Restaura dados de um backup JSON (fixtures)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fixture',
            default='initial_data.json',
            help='Nome do arquivo fixture (padrão: initial_data.json)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra o que seria feito, sem executar'
        )

    def handle(self, *args, **options):
        fixture_name = options['fixture']
        dry_run = options['dry_run']
        
        # Verificar se fixture existe
        from django.conf import settings
        
        # Procurar em todas as apps
        fixture_path = None
        for app_config in settings.INSTALLED_APPS:
            if '.' in app_config:
                app_name = app_config.split('.')[-1]
            else:
                app_name = app_config
            
            # Verificar pasta fixtures da app
            possible_path = Path(settings.BASE_DIR) / app_name / 'fixtures' / fixture_name
            if possible_path.exists():
                fixture_path = possible_path
                break
        
        # Verificar pasta core/fixtures
        if not fixture_path:
            core_path = Path(settings.BASE_DIR) / 'core' / 'fixtures' / fixture_name
            if core_path.exists():
                fixture_path = core_path
        
        if not fixture_path:
            self.stdout.write(
                self.style.ERROR(f'❌ Fixture não encontrada: {fixture_name}')
            )
            return
        
        self.stdout.write(f'📂 Fixture encontrada: {fixture_path}')
        self.stdout.write(f'   Tamanho: {fixture_path.stat().st_size / 1024:.1f} KB')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 Modo dry-run: nenhuma alteração será feita'))
            return
        
        try:
            self.stdout.write('⏳ Carregando dados...')
            call_command('loaddata', str(fixture_path), verbosity=1)
            self.stdout.write(self.style.SUCCESS('✅ Dados restaurados com sucesso!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao restaurar: {e}'))
            raise
