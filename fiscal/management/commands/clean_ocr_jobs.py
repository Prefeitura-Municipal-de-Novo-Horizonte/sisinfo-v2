"""
Management command para limpar OCRJobs antigos.
Remove jobs completados/falhos mais antigos que X dias.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from fiscal.models import OCRJob


class Command(BaseCommand):
    help = 'Limpa OCRJobs antigos (completados/falhos mais de X dias)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Deletar jobs mais antigos que X dias (padrão: 7)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Deletar TODOS os jobs, incluindo pending/processing'
        )
        parser.add_argument(
            '--stale',
            action='store_true',
            help='Deletar jobs "travados" (pending/processing por mais de 1 hora)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostra o que seria deletado sem efetivamente deletar'
        )
        parser.add_argument(
            '--with-images',
            action='store_true',
            help='Também deleta imagens do Supabase Storage'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        delete_all = options['all']
        delete_stale = options['stale']
        with_images = options['with_images']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        stale_cutoff = timezone.now() - timedelta(hours=1)
        
        # Query base
        if delete_all:
            jobs = list(OCRJob.objects.filter(created_at__lt=cutoff_date))
            self.stdout.write(f"Buscando TODOS os jobs mais antigos que {days} dias...")
        else:
            jobs = list(OCRJob.objects.filter(
                status__in=['completed', 'failed'],
                created_at__lt=cutoff_date
            ))
            self.stdout.write(f"Buscando jobs completados/falhos mais antigos que {days} dias...")
        
        # Jobs travados (stale)
        stale_jobs = []
        if delete_stale:
            stale_jobs = list(OCRJob.objects.filter(
                status__in=['pending', 'processing'],
                created_at__lt=stale_cutoff
            ))
        
        # Contagem
        jobs_count = len(jobs)
        stale_count = len(stale_jobs)
        
        if jobs_count == 0 and stale_count == 0:
            self.stdout.write(self.style.SUCCESS("Nenhum job para limpar."))
            return
        
        self.stdout.write(f"  - Jobs regulares encontrados: {jobs_count}")
        if delete_stale:
            self.stdout.write(f"  - Jobs travados encontrados: {stale_count}")
        if with_images:
            self.stdout.write(self.style.WARNING("  - Imagens do Storage serão deletadas!"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] Nenhum job foi deletado."))
            
            if jobs_count > 0:
                self.stdout.write("\nJobs que seriam deletados:")
                for job in jobs[:10]:
                    self.stdout.write(f"  - {job.id} | {job.status} | {job.created_at}")
                if jobs_count > 10:
                    self.stdout.write(f"  ... e mais {jobs_count - 10} jobs")
            
            if stale_count > 0:
                self.stdout.write("\nJobs travados que seriam deletados:")
                for job in stale_jobs[:10]:
                    self.stdout.write(f"  - {job.id} | {job.status} | {job.created_at}")
        else:
            from fiscal.services.storage import delete_image_from_storage
            
            deleted_count = 0
            error_count = 0
            
            all_jobs = jobs + stale_jobs
            
            for job in all_jobs:
                try:
                    # Deletar imagem do Storage se solicitado
                    if with_images and job.image_path:
                        if delete_image_from_storage(job.image_path):
                            self.stdout.write(f"  Imagem {job.image_path} deletada")
                    
                    # Deletar o job
                    job.delete()
                    deleted_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Erro ao deletar job {job.id}: {e}"))
                    error_count += 1
            
            self.stdout.write(self.style.SUCCESS(f"\n✅ {deleted_count} jobs deletados com sucesso!"))
            if error_count > 0:
                self.stdout.write(self.style.WARNING(f"⚠️ {error_count} erros durante exclusão"))
