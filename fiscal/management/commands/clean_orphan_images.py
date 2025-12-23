"""
Limpa imagens órfãs do Supabase Storage.
Identifica imagens no bucket que não estão vinculadas a nenhuma Invoice ou OCRJob.
"""
import requests
from django.core.management.base import BaseCommand
from decouple import config

from fiscal.models import Invoice, OCRJob


class Command(BaseCommand):
    help = 'Remove imagens órfãs do Supabase Storage (não vinculadas a Invoice ou OCRJob)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas lista as imagens órfãs sem deletar'
        )
        parser.add_argument(
            '--bucket',
            default='ocr-images',
            help='Nome do bucket (default: ocr-images)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        bucket = options['bucket']
        
        # Configuração Supabase
        supabase_url = config('SUPABASE_URL', default='')
        service_key = config('SUPABASE_SERVICE_ROLE_KEY', default='')
        
        if not supabase_url or not service_key:
            self.stderr.write(self.style.ERROR('Supabase não configurado'))
            return
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"🔍 Analisando bucket: {bucket}")
        self.stdout.write(f"{'='*60}\n")
        
        # 1. Listar todas as imagens no bucket
        storage_images = self._list_bucket_images(supabase_url, service_key, bucket)
        
        if not storage_images:
            self.stdout.write(self.style.SUCCESS('Nenhuma imagem encontrada no bucket.'))
            return
        
        self.stdout.write(f"📦 Total de imagens no Storage: {len(storage_images)}")
        
        # 2. Buscar imagens referenciadas no banco
        invoice_photos = set(
            Invoice.objects.exclude(photo__isnull=True)
            .exclude(photo='')
            .values_list('photo', flat=True)
        )
        
        ocr_paths = set(
            OCRJob.objects.exclude(image_path__isnull=True)
            .exclude(image_path='')
            .values_list('image_path', flat=True)
        )
        
        db_images = invoice_photos | ocr_paths
        self.stdout.write(f"🗄️  Imagens referenciadas no banco: {len(db_images)}")
        
        # 3. Identificar órfãs
        orphan_images = [img for img in storage_images if img not in db_images]
        
        self.stdout.write(f"🗑️  Imagens órfãs encontradas: {len(orphan_images)}")
        
        if not orphan_images:
            self.stdout.write(self.style.SUCCESS('\n✅ Nenhuma imagem órfã encontrada!'))
            return
        
        # 4. Listar/Deletar órfãs
        self.stdout.write(f"\n{'='*60}")
        
        deleted = 0
        for img in orphan_images:
            if dry_run:
                self.stdout.write(f"  [DRY-RUN] Seria deletado: {img}")
            else:
                if self._delete_image(supabase_url, service_key, bucket, img):
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Deletado: {img}"))
                    deleted += 1
                else:
                    self.stdout.write(self.style.ERROR(f"  ✗ Falha ao deletar: {img}"))
        
        # 5. Resumo
        self.stdout.write(f"\n{'='*60}")
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"[DRY-RUN] {len(orphan_images)} imagens seriam deletadas. "
                f"Execute sem --dry-run para deletar."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"✅ {deleted}/{len(orphan_images)} imagens órfãs removidas!"
            ))

    def _list_bucket_images(self, supabase_url, service_key, bucket):
        """Lista todas as imagens no bucket."""
        try:
            url = f"{supabase_url}/storage/v1/object/list/{bucket}"
            
            response = requests.post(
                url,
                headers={
                    'Authorization': f'Bearer {service_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'prefix': '',
                    'limit': 10000,  # Máximo
                },
                timeout=60
            )
            
            if response.status_code == 200:
                items = response.json()
                # Retorna apenas nomes de arquivos (não pastas)
                return [item['name'] for item in items if item.get('name')]
            else:
                self.stderr.write(f"Erro ao listar bucket: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.stderr.write(f"Exceção ao listar bucket: {e}")
            return []

    def _delete_image(self, supabase_url, service_key, bucket, filename):
        """Deleta uma imagem do bucket."""
        try:
            url = f"{supabase_url}/storage/v1/object/{bucket}/{filename}"
            
            response = requests.delete(
                url,
                headers={
                    'Authorization': f'Bearer {service_key}',
                },
                timeout=30
            )
            
            return response.status_code in [200, 204]
            
        except Exception as e:
            self.stderr.write(f"Exceção ao deletar {filename}: {e}")
            return False
