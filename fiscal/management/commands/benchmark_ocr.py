
from django.core.management.base import BaseCommand
from pathlib import Path
from fiscal.services.ocr import InvoiceOCRService
from django.conf import settings

class Command(BaseCommand):
    help = 'Executa benchmark de OCR nas notas fiscais de backup'

    def handle(self, *args, **options):
        # Caminho absoluto para a pasta de backups
        backup_dir = settings.BASE_DIR / 'backups' / 'notas'
        
        if not backup_dir.exists():
            self.stdout.write(self.style.ERROR(f"Diretório não encontrado: {backup_dir}"))
            return

        files = list(backup_dir.glob('*'))
        total = len(files)
        success = 0
        failures = []

        self.stdout.write(f"Iniciando benchmark de OCR em {total} arquivos...\n")

        service = InvoiceOCRService()

        for i, file_path in enumerate(files, 1):
            self.stdout.write(f"Processando ({i}/{total}): {file_path.name}...")
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    # Determinar mime type grosso modo
                    mime_type = "image/jpeg" if file_path.suffix.lower() in ['.jpg', '.jpeg'] else "image/png"
                    
                    result = service.extract_from_bytes(content, mime_type=mime_type)
                    
                    if result and result.number and result.confidence > 0.5:
                        item_count = len(result.products)
                        self.stdout.write(self.style.SUCCESS(f"  [OK] Lido: {result.number} - {result.supplier_name}"))
                        self.stdout.write(f"       Itens: {item_count} | Total: {result.total_value}")
                        
                        if item_count == 0:
                            self.stdout.write(self.style.WARNING("       [AVISO] Nenhum item extraído (!)"))
                        
                        success += 1
                    else:
                        error_msg = result.error if hasattr(result, 'error') else 'Desconhecido'
                        self.stdout.write(self.style.ERROR(f"  [FALHA] Confiança baixa ou dados faltantes: {error_msg}"))
                        if hasattr(result, 'raw_text'):
                             self.stdout.write(f"   Raw text preview: {result.raw_text[:100]}...")
                        failures.append(file_path.name)
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [ERRO] {e}"))
                failures.append(file_path.name)

        self.stdout.write("\nBenchmark Concluído")
        percent = (success/total*100) if total > 0 else 0
        self.stdout.write(f"Taxa de Sucesso: {success}/{total} ({percent:.1f}%)")
        
        if failures:
            self.stdout.write(self.style.ERROR("Arquivos com falha:"))
            for name in failures:
                self.stdout.write(f" - {name}")
