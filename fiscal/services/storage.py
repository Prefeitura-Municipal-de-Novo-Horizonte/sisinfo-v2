"""
Serviço para gerenciar imagens no Supabase Storage.
Inclui funções para upload, download e exclusão de imagens.
"""
import requests
from decouple import config


def _get_supabase_config():
    """Retorna configurações do Supabase."""
    return {
        'url': config('SUPABASE_URL', default=''),
        'service_key': config('SUPABASE_SERVICE_ROLE_KEY', default=''),
    }


def is_supabase_configured():
    """Verifica se Supabase está configurado."""
    conf = _get_supabase_config()
    return bool(conf['url'] and conf['service_key'])


def delete_image_from_storage(image_path: str) -> bool:
    """
    Deleta uma imagem do Supabase Storage.
    
    Args:
        image_path: Nome do arquivo no bucket ocr-images
        
    Returns:
        True se deletou com sucesso, False caso contrário
    """
    if not image_path or image_path.startswith('local/'):
        # Imagem local ou path vazio, não precisa deletar do Supabase
        return True
    
    conf = _get_supabase_config()
    if not conf['url'] or not conf['service_key']:
        print("Supabase não configurado, pulando exclusão de imagem")
        return False
    
    try:
        # API de deleção do Supabase Storage
        url = f"{conf['url']}/storage/v1/object/ocr-images/{image_path}"
        
        response = requests.delete(
            url,
            headers={
                'Authorization': f"Bearer {conf['service_key']}",
            },
            timeout=30
        )
        
        if response.status_code in [200, 204]:
            print(f"Supabase Storage: Imagem {image_path} deletada com sucesso")
            return True
        elif response.status_code == 404:
            # Já não existe, tudo bem
            print(f"Supabase Storage: Imagem {image_path} não encontrada (já deletada?)")
            return True
        else:
            print(f"Supabase Storage Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Supabase Storage Delete Exception: {e}")
        return False


def check_image_exists(filename: str) -> bool:
    """
    Verifica se uma imagem já existe no bucket.
    
    Args:
        filename: Nome do arquivo no bucket
        
    Returns:
        True se existe, False caso contrário
    """
    conf = _get_supabase_config()
    if not conf['url'] or not conf['service_key']:
        return False
    
    try:
        # Tentar fazer HEAD request para verificar se existe
        url = f"{conf['url']}/storage/v1/object/info/ocr-images/{filename}"
        
        response = requests.get(
            url,
            headers={
                'Authorization': f"Bearer {conf['service_key']}",
            },
            timeout=10
        )
        
        return response.status_code == 200
        
    except Exception:
        return False


def cleanup_ocr_job(job_id: str, delete_image: bool = True) -> bool:
    """
    Limpa um OCRJob e opcionalmente sua imagem.
    
    Args:
        job_id: UUID do OCRJob
        delete_image: Se True, deleta a imagem do Storage também
        
    Returns:
        True se limpou com sucesso
    """
    from fiscal.models import OCRJob
    
    try:
        job = OCRJob.objects.get(id=job_id)
        
        # Deletar imagem do Storage se solicitado
        if delete_image and job.image_path:
            delete_image_from_storage(job.image_path)
        
        # Deletar o job
        job.delete()
        print(f"OCRJob {job_id} removido com sucesso")
        return True
        
    except OCRJob.DoesNotExist:
        print(f"OCRJob {job_id} não encontrado")
        return False
    except Exception as e:
        print(f"Erro ao limpar OCRJob {job_id}: {e}")
        return False


def cleanup_stale_jobs(hours: int = 1) -> int:
    """
    Limpa jobs órfãos (pending/processing por muito tempo).
    
    Args:
        hours: Jobs mais antigos que X horas serão removidos
        
    Returns:
        Número de jobs removidos
    """
    from datetime import timedelta
    from django.utils import timezone
    from fiscal.models import OCRJob
    
    cutoff = timezone.now() - timedelta(hours=hours)
    
    stale_jobs = OCRJob.objects.filter(
        status__in=['pending', 'processing'],
        created_at__lt=cutoff
    )
    
    count = 0
    for job in stale_jobs:
        if cleanup_ocr_job(str(job.id), delete_image=True):
            count += 1
    
    return count
