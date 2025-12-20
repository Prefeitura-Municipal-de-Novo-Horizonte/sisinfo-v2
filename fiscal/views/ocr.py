"""
Views para OCR assíncrono com polling.
Contorna o limite de 10s da Vercel dividindo o processo em múltiplas requests.
"""
import json
import traceback
from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from PIL import Image

from fiscal.models import OCRJob


@login_required(login_url='authenticate:login')
def ocr_submit(request):
    """
    Endpoint 1: Submete imagem para OCR.
    Salva imagem, cria OCRJob(pending), retorna job_id.
    Tempo esperado: ~2s (bem abaixo do limite de 10s)
    
    POST /fiscal/ocr/submit/
    Body: multipart/form-data com campo 'photo'
    Response: { job_id: "uuid" }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    photo = request.FILES.get('photo')
    if not photo:
        return JsonResponse({'error': 'Nenhuma imagem enviada'}, status=400)
    
    try:
        # 1. Otimizar imagem (mesma lógica do invoice_process)
        img = Image.open(photo)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionar para max 800px
        max_size = 800
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size))
        
        output = BytesIO()
        img.save(output, format='JPEG', quality=50)
        output.seek(0)
        image_bytes = output.getvalue()
        
        # 2. Salvar imagem (local ou Cloudinary)
        import uuid as uuid_lib
        
        if getattr(settings, 'USE_CLOUDINARY', False):
            # PRODUÇÃO: Upload para Cloudinary
            import cloudinary.uploader
            upload_result = cloudinary.uploader.upload(
                image_bytes,
                folder='sisinfo/ocr_jobs',
                resource_type='image'
            )
            image_path = upload_result.get('public_id')
        else:
            # DESENVOLVIMENTO: Salvar localmente
            from pathlib import Path
            
            upload_dir = settings.MEDIA_ROOT / 'ocr_jobs'
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{uuid_lib.uuid4()}.jpg"
            file_path = upload_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            image_path = f"local/ocr_jobs/{filename}"
        
        # 3. Criar OCRJob
        job = OCRJob.objects.create(
            image_path=image_path,
            status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'job_id': str(job.id)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Erro ao salvar imagem: {str(e)}'
        }, status=500)


@login_required(login_url='authenticate:login')
def ocr_status(request, job_id):
    """
    Endpoint 2: Verifica status do job e dispara processamento se necessário.
    
    GET /fiscal/ocr/status/<job_id>/
    Response:
        - pending/processing: { status: "processing", progress: "Lendo nota..." }
        - completed: { status: "completed", data: {...} }
        - failed: { status: "failed", error: "..." }
    
    Se o job está 'pending', esta view INICIA o processamento OCR.
    Isso é o "self-triggering" que dispensa Cron Jobs.
    """
    try:
        job = OCRJob.objects.get(id=job_id)
    except OCRJob.DoesNotExist:
        return JsonResponse({'error': 'Job não encontrado'}, status=404)
    
    # Se o job está pendente, iniciar processamento
    if job.status == 'pending':
        # Marcar como processing antes de iniciar
        job.mark_processing()
        
        # Processar OCR (executa na mesma request)
        try:
            result = _process_ocr_job(job)
            
            if result.get('success'):
                job.mark_completed(result['data'])
            else:
                job.mark_failed(result.get('error', 'Erro desconhecido'))
        except Exception as e:
            job.mark_failed(str(e))
        
        # Recarregar job para ter status atualizado
        job.refresh_from_db()
    
    # Retornar status atual
    if job.status == 'processing':
        return JsonResponse({
            'status': 'processing',
            'progress': 'Lendo nota fiscal...'
        })
    
    elif job.status == 'completed':
        return JsonResponse({
            'status': 'completed',
            'data': job.result
        })
    
    elif job.status == 'failed':
        return JsonResponse({
            'status': 'failed',
            'error': job.error_message
        })
    
    # Fallback
    return JsonResponse({
        'status': job.status,
        'progress': 'Processando...'
    })


def _process_ocr_job(job: OCRJob) -> dict:
    """
    Processa o OCR de um job.
    Retorna dict com 'success' e 'data' ou 'error'.
    """
    from fiscal.services.ocr import (
        InvoiceOCRService, 
        find_supplier_by_cnpj, 
        find_similar_materials
    )
    from fiscal.models import Invoice
    
    try:
        # 1. Recuperar imagem
        image_bytes = _get_image_bytes(job.image_path)
        
        if not image_bytes:
            return {'success': False, 'error': 'Não foi possível carregar a imagem'}
        
        # 2. Executar OCR
        ocr_service = InvoiceOCRService()
        extracted = ocr_service.extract_from_bytes(image_bytes, mime_type='image/jpeg')
        
        if extracted.error:
            # Verificar se é erro de quota
            if '429' in extracted.error or 'quota' in extracted.error.lower():
                return {
                    'success': False, 
                    'error': 'Limite diário de OCR atingido. Cadastre manualmente.',
                    'error_type': 'quota_exceeded'
                }
            return {'success': False, 'error': extracted.error}
        
        # 3. Verificar duplicidade
        existing = Invoice.objects.filter(
            number=extracted.number,
            supplier__cnpj__icontains=extracted.supplier_cnpj[:8] if extracted.supplier_cnpj else ''
        ).first()
        
        if existing:
            return {
                'success': False, 
                'error': f'Nota {extracted.number} já cadastrada para este fornecedor'
            }
        
        # 4. Buscar fornecedor pelo CNPJ
        supplier = find_supplier_by_cnpj(extracted.supplier_cnpj)
        supplier_data = None
        if supplier:
            supplier_data = {
                'id': supplier.id,
                'name': supplier.trade or supplier.company,
                'cnpj': supplier.cnpj
            }
        
        # 5. Processar materiais (busca sugestões se tiver fornecedor)
        materials_suggestions = []
        for product in extracted.products:
            suggestions = []
            if supplier:
                similar = find_similar_materials(product.description, supplier.id, limit=5)
                suggestions = [
                    {
                        'id': m.id,
                        'name': m.material.name,
                        'bidding': m.bidding.name,
                        'price': str(m.price),
                        'available': m.available_for_purchase,
                    }
                    for m in similar
                ]
            
            materials_suggestions.append({
                'product': {
                    'code': product.code,
                    'description': product.description,
                    'quantity': product.quantity,
                    'unit': product.unit,
                    'unit_price': product.unit_price,
                    'total_price': product.total_price,
                },
                'suggestions': suggestions,
                'selected_material': None
            })
        
        # 6. Montar resposta completa
        return {
            'success': True,
            'data': {
                'photo_url': _get_image_url(job.image_path),
                'photo_public_id': job.image_path,
                'number': extracted.number,
                'series': extracted.series,
                'access_key': extracted.access_key,
                'issue_date': extracted.issue_date,
                'total_value': extracted.total_value,
                'supplier': supplier_data,
                'supplier_name_detected': extracted.supplier_name,
                'supplier_cnpj_detected': extracted.supplier_cnpj,
                'materials': materials_suggestions,
                'observations': extracted.observations,
                'confidence': extracted.confidence,
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def _get_image_bytes(image_path: str) -> bytes | None:
    """Recupera bytes da imagem a partir do path (local ou Cloudinary)."""
    import urllib.request
    
    try:
        if image_path.startswith('local/'):
            # Arquivo local
            from pathlib import Path
            
            relative_path = image_path.replace('local/', '')
            file_path = settings.MEDIA_ROOT / relative_path
            
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    return f.read()
            return None
        else:
            # Cloudinary - construir URL e baixar
            import cloudinary
            
            url = cloudinary.CloudinaryImage(image_path).build_url()
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read()
                
    except Exception as e:
        print(f"Erro ao recuperar imagem: {e}")
        return None


def _get_image_url(image_path: str) -> str:
    """Retorna URL pública da imagem."""
    if image_path.startswith('local/'):
        relative_path = image_path.replace('local/', '')
        return f"{settings.MEDIA_URL}{relative_path}"
    else:
        import cloudinary
        return cloudinary.CloudinaryImage(image_path).build_url()
