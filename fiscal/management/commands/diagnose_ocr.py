
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from fiscal.services.ocr import InvoiceOCRService

class Command(BaseCommand):
    help = 'Diagnostica falhas de OCR em arquivos específicos'

    def add_arguments(self, parser):
        parser.add_argument('filenames', nargs='+', type=str, help='Nomes dos arquivos na pasta backups/notas para testar')

    def handle(self, *args, **options):
        filenames = options['filenames']
        base_path = settings.BASE_DIR / 'backups' / 'notas'
        service = InvoiceOCRService()
        
        for filename in filenames:
            file_path = base_path / filename
            self.stdout.write(self.style.MIGRATE_HEADING(f"\n--- Verificando {filename} ---"))
            
            if not file_path.exists():
                self.stdout.write(self.style.ERROR(f"Arquivo não encontrado: {file_path}"))
                continue
                
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    mime_type = "image/jpeg" if file_path.suffix.lower() in ['.jpg', '.jpeg'] else "image/png"
                    
                    result = service.extract_from_bytes(content, mime_type=mime_type)
                    
                    response_data = {
                        'number': result.number,
                        'series': result.series,
                        'access_key': result.access_key,
                        'issue_date': result.issue_date,
                        'total_value': result.total_value,
                        'supplier_name_detected': result.supplier_name,
                        'supplier_cnpj_detected': result.supplier_cnpj,
                        'confidence': result.confidence,
                        'items_count': len(result.products),
                        'error': result.error
                    }
                    
                    self.stdout.write(json.dumps(response_data, indent=2, ensure_ascii=False))
                    
            except Exception as e:
                 self.stdout.write(self.style.ERROR(f"ERRO: {e}"))
