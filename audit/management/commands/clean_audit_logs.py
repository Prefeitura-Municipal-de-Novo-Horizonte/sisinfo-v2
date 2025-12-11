"""
Comando para limpar logs antigos de auditoria do MongoDB.
"""
from django.core.management.base import BaseCommand
from audit.mongodb import MongoDBConnection
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Limpa logs de auditoria antigos do MongoDB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Remover logs mais antigos que X dias (padrão: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria deletado sem deletar'
        )
        parser.add_argument(
            '--backup-first',
            action='store_true',
            help='Faz backup antes de limpar'
        )

    def handle(self, *args, **options):
        try:
            # Conecta ao MongoDB
            mongo = MongoDBConnection()
            if not mongo.logs:
                self.stdout.write(self.style.ERROR('MongoDB não disponível'))
                return

            days = options['days']
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Conta logs a serem removidos
            query = {'timestamp': {'$lt': cutoff_date}}
            count = mongo.logs.count_documents(query)

            if count == 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Nenhum log com mais de {days} dias encontrado')
                )
                return

            self.stdout.write(
                self.style.WARNING(
                    f'Encontrados {count} logs com mais de {days} dias'
                )
            )

            # Dry-run
            if options['dry_run']:
                self.stdout.write(
                    self.style.NOTICE(
                        f'[DRY-RUN] {count} logs seriam removidos (não foram deletados)'
                    )
                )
                return

            # Backup primeiro
            if options['backup_first']:
                self.stdout.write('Fazendo backup antes de limpar...')
                try:
                    subprocess.run(
                        ['python', 'manage.py', 'backup_audit_logs', '--days', str(days)],
                        check=True
                    )
                    self.stdout.write(self.style.SUCCESS('✓ Backup concluído'))
                except subprocess.CalledProcessError as e:
                    self.stdout.write(self.style.ERROR(f'Erro no backup: {e}'))
                    return

            # Confirmação
            confirm = input(f'Confirma a remoção de {count} logs? (sim/não): ')
            if confirm.lower() not in ['sim', 's', 'yes', 'y']:
                self.stdout.write(self.style.NOTICE('Operação cancelada'))
                return

            # Remove logs
            self.stdout.write('Removendo logs...')
            result = mongo.logs.delete_many(query)

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ {result.deleted_count} logs removidos com sucesso'
                )
            )

        except Exception as e:
            logger.error(f'Erro ao limpar logs: {e}')
            self.stdout.write(self.style.ERROR(f'Erro: {e}'))
