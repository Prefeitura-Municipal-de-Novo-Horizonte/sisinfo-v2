"""
Comando para fazer backup dos logs de auditoria do MongoDB.
"""
from django.core.management.base import BaseCommand
from audit.mongodb import MongoDBConnection
from datetime import datetime, timedelta
from pathlib import Path
import json
import gzip
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Faz backup dos logs de auditoria do MongoDB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Caminho do arquivo de saída (padrão: backups/audit_logs_YYYY-MM-DD.json)'
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Número de dias para incluir no backup (padrão: todos)'
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Filtrar por modelo específico'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Comprimir arquivo de saída com gzip'
        )

    def handle(self, *args, **options):
        try:
            # Conecta ao MongoDB
            mongo = MongoDBConnection()
            if not mongo.logs:
                self.stdout.write(self.style.ERROR('MongoDB não disponível'))
                return

            # Monta filtro
            query = {}
            if options['days']:
                cutoff_date = datetime.utcnow() - timedelta(days=options['days'])
                query['timestamp'] = {'$gte': cutoff_date}
            
            if options['model']:
                query['model'] = options['model']

            # Busca logs
            self.stdout.write('Buscando logs...')
            logs = list(mongo.logs.find(query))
            
            # Converte ObjectId para string
            for log in logs:
                log['_id'] = str(log['_id'])
                if 'timestamp' in log:
                    log['timestamp'] = log['timestamp'].isoformat()

            # Define arquivo de saída
            if options['output']:
                output_path = Path(options['output'])
            else:
                backup_dir = Path('backups')
                backup_dir.mkdir(exist_ok=True)
                filename = f"audit_logs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
                output_path = backup_dir / filename

            # Salva arquivo
            self.stdout.write(f'Salvando {len(logs)} logs em {output_path}...')
            
            if options['compress']:
                output_path = output_path.with_suffix('.json.gz')
                with gzip.open(output_path, 'wt', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Backup concluído: {len(logs)} logs salvos em {output_path}'
                )
            )

        except Exception as e:
            logger.error(f'Erro ao fazer backup: {e}')
            self.stdout.write(self.style.ERROR(f'Erro: {e}'))
