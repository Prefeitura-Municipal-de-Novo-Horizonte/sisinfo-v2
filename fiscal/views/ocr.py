"""
Views para OCR assíncrono com Supabase Edge Functions.
Contorna o limite de 10s da Vercel usando:
1. Upload para Supabase Storage
2. Invocação de Edge Function (150s timeout)
3. Polling do status do job
"""
import json
import traceback
import requests
from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decouple import config
from PIL import Image

from fiscal.models import OCRJob


def _get_supabase_config():
    """Retorna configurações do Supabase."""
    return {
        'url': config('SUPABASE_URL', default=''),
        'anon_key': config('SUPABASE_ANON_KEY', default=''),
        'service_key': config('SUPABASE_SERVICE_ROLE_KEY', default=''),
    }


def _use_supabase():
    """Verifica se Supabase está configurado."""
    conf = _get_supabase_config()
    return bool(conf['url'] and conf['service_key'])


@login_required(login_url='authenticate:login')
def ocr_submit(request):
    """
    Submete imagem para OCR via Supabase Edge Function.
    
    Fluxo:
    1. Otimiza imagem
    2. Upload para Supabase Storage (bucket: ocr-images)
    3. Cria OCRJob no banco
    4. Invoca Edge Function (fire-and-forget)
    5. Retorna job_id para polling
    
    Tempo esperado: ~3s (bem abaixo do limite de 10s da Vercel)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    photo = request.FILES.get('photo')
    if not photo:
        return JsonResponse({'error': 'Nenhuma imagem enviada'}, status=400)
    
    try:
        # 1. Ler bytes originais para calcular hash (ANTES de otimizar)
        import hashlib
        original_bytes = photo.read()
        image_hash = hashlib.md5(original_bytes).hexdigest()
        photo.seek(0)  # Voltar ao início para poder abrir com PIL
        
        # 2. Otimizar imagem
        img = Image.open(photo)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        max_size = 800
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size))
        
        output = BytesIO()
        img.save(output, format='JPEG', quality=50)
        output.seek(0)
        image_bytes = output.getvalue()
        
        # 3. Verificar se já existe um job com esta imagem que foi concluído com sucesso
        print(f"DEBUG OCR: Hash da imagem: {image_hash}")
        
        existing_job = OCRJob.objects.filter(
            image_hash=image_hash,
            status='completed'
        ).first()
        
        print(f"DEBUG OCR: Job existente com este hash: {existing_job}")
        
        if existing_job:
            # Já processamos esta imagem! Retornar os dados existentes
            result_data = existing_job.result or {}
            
            # Verificar se a nota já foi cadastrada no sistema
            access_key = result_data.get('access_key', '')
            number = result_data.get('number', '')
            
            from fiscal.models import Invoice
            
            # Buscar nota existente pela chave de acesso ou número
            existing_invoice = None
            if access_key:
                existing_invoice = Invoice.objects.filter(access_key=access_key).first()
            if not existing_invoice and number:
                existing_invoice = Invoice.objects.filter(number=number).first()
            
            if existing_invoice:
                return JsonResponse({
                    'error': f'Esta nota fiscal já está cadastrada no sistema (NF {existing_invoice.number} - {existing_invoice.supplier}).',
                    'duplicate': True,
                    'invoice_id': existing_invoice.pk
                }, status=400)
            else:
                # Imagem já processada mas nota não foi salva - reusar resultado
                # Fazer upload da nova imagem para garantir que esteja disponível
                import uuid as uuid_lib
                new_filename = f"{uuid_lib.uuid4()}.jpg"
                
                if _use_supabase():
                    new_image_path = _upload_to_supabase_storage(image_bytes, new_filename)
                    if new_image_path:
                        # Atualizar o job com o novo path da imagem
                        existing_job.image_path = new_image_path
                        existing_job.save(update_fields=['image_path'])
                else:
                    # Local: salvar imagem localmente
                    from pathlib import Path
                    upload_dir = settings.MEDIA_ROOT / 'ocr_jobs'
                    upload_dir.mkdir(parents=True, exist_ok=True)
                    file_path = upload_dir / new_filename
                    with open(file_path, 'wb') as f:
                        f.write(image_bytes)
                    existing_job.image_path = f"local/ocr_jobs/{new_filename}"
                    existing_job.save(update_fields=['image_path'])
                
                return JsonResponse({
                    'success': True,
                    'job_id': str(existing_job.id),
                    'reused': True,
                    'message': 'Dados recuperados de processamento anterior'
                })
        
        # 4. Gerar nome único para a imagem
        import uuid as uuid_lib
        filename = f"{uuid_lib.uuid4()}.jpg"
        
        # 5. Upload e criação do job
        if _use_supabase():
            # PRODUÇÃO: Upload para Supabase Storage
            image_path = _upload_to_supabase_storage(image_bytes, filename)
            
            if not image_path:
                return JsonResponse({
                    'error': 'Erro ao fazer upload da imagem para o Storage'
                }, status=500)
            
            # Criar OCRJob com hash
            job = OCRJob.objects.create(
                image_path=image_path,
                image_hash=image_hash,
                status='pending'
            )
            
            # Invocar Edge Function (fire-and-forget)
            _invoke_edge_function(str(job.id), image_path)
            
        else:
            # DESENVOLVIMENTO LOCAL: Salvar localmente
            from pathlib import Path
            
            upload_dir = settings.MEDIA_ROOT / 'ocr_jobs'
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = upload_dir / filename
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            image_path = f"local/ocr_jobs/{filename}"
            
            job = OCRJob.objects.create(
                image_path=image_path,
                image_hash=image_hash,
                status='pending'
            )
        
        return JsonResponse({
            'success': True,
            'job_id': str(job.id)
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'error': f'Erro ao processar imagem: {str(e)}'
        }, status=500)



def _upload_to_supabase_storage(image_bytes: bytes, filename: str) -> str | None:
    """
    Faz upload da imagem para o Supabase Storage.
    Retorna o path da imagem ou None em caso de erro.
    """
    conf = _get_supabase_config()
    
    try:
        # Supabase Storage API endpoint
        url = f"{conf['url']}/storage/v1/object/ocr-images/{filename}"
        
        response = requests.post(
            url,
            headers={
                'Authorization': f"Bearer {conf['service_key']}",
                'Content-Type': 'image/jpeg',
                'x-upsert': 'true',  # Sobrescreve se existir
            },
            data=image_bytes,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print(f"Supabase Storage: Upload OK - {filename}")
            return filename
        else:
            print(f"Supabase Storage Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Supabase Storage Exception: {e}")
        return None


def _invoke_edge_function(job_id: str, image_path: str):
    """
    Invoca a Edge Function process-ocr de forma assíncrona (fire-and-forget).
    Não espera a resposta, pois o processamento pode demorar.
    Envia TODAS as chaves Gemini para permitir rotação na Edge Function.
    """
    conf = _get_supabase_config()
    gemini_keys = config('GEMINI_API_KEY', default='')
    
    # Enviar todas as chaves (a Edge Function faz a rotação)
    # Não precisa processar aqui, a Edge Function aceita qualquer formato
    
    try:
        url = f"{conf['url']}/functions/v1/process-ocr"
        
        # Fire-and-forget: timeout muito curto, ignora resposta
        requests.post(
            url,
            headers={
                'Authorization': f"Bearer {conf['anon_key']}",
                'Content-Type': 'application/json',
            },
            json={
                'job_id': job_id,
                'image_path': image_path,
                'gemini_keys': gemini_keys,  # Todas as chaves
            },
            timeout=2  # Timeout curto - não esperamos a resposta
        )
    except requests.Timeout:
        # Esperado - a function continua rodando no Supabase
        pass
    except Exception as e:
        print(f"Edge Function invoke error (non-fatal): {e}")


@login_required(login_url='authenticate:login')
def ocr_status(request, job_id):
    """
    Verifica status do job de OCR.
    
    GET /fiscal/ocr/status/<job_id>/
    
    Respostas:
    - pending: { status: "pending", progress: "Aguardando..." }
    - processing: { status: "processing", progress: "Lendo nota fiscal..." }
    - completed: { status: "completed", data: {...} }
    - failed: { status: "failed", error: "..." }
    
    NOTA: Com Supabase Edge Functions, o processamento ocorre no Supabase,
    não mais nesta view. Esta view apenas consulta o status no banco.
    
    Para desenvolvimento LOCAL (sem Supabase), ainda processa aqui.
    """
    try:
        job = OCRJob.objects.get(id=job_id)
    except OCRJob.DoesNotExist:
        return JsonResponse({'error': 'Job não encontrado'}, status=404)
    
    # Se está em desenvolvimento local e job está pending, processar aqui
    if not _use_supabase() and job.status == 'pending':
        job.mark_processing()
        
        try:
            result = _process_ocr_job_locally(job)
            
            if result.get('success'):
                job.mark_completed(result['data'])
            else:
                job.mark_failed(result.get('error', 'Erro desconhecido'))
        except Exception as e:
            job.mark_failed(str(e))
        
        job.refresh_from_db()
    
    # Retornar status atual
    if job.status == 'pending':
        return JsonResponse({
            'status': 'pending',
            'progress': 'Aguardando processamento...'
        })
    
    elif job.status == 'processing':
        return JsonResponse({
            'status': 'processing',
            'progress': 'Lendo nota fiscal...'
        })
    
    elif job.status == 'completed':
        # Buscar dados adicionais (fornecedor, sugestões de materiais)
        result_data = _enrich_ocr_result(job)
        # Adicionar job_id para o frontend poder limpar depois se necessário
        result_data['job_id'] = str(job.id)
        return JsonResponse({
            'status': 'completed',
            'data': result_data
        })
    
    elif job.status == 'failed':
        return JsonResponse({
            'status': 'failed',
            'error': job.error_message
        })
    
    return JsonResponse({
        'status': job.status,
        'progress': 'Processando...'
    })


def _enrich_ocr_result(job: OCRJob) -> dict:
    """
    Enriquece o resultado do OCR com dados adicionais do banco.
    - Busca fornecedor pelo CNPJ
    - Busca sugestões de materiais
    """
    from fiscal.services.ocr import find_supplier_by_cnpj, find_similar_materials
    
    result = job.result or {}
    
    # Buscar fornecedor pelo CNPJ
    supplier_cnpj = result.get('supplier_cnpj', '')
    supplier = find_supplier_by_cnpj(supplier_cnpj) if supplier_cnpj else None
    
    supplier_data = None
    if supplier:
        supplier_data = {
            'id': supplier.id,
            'name': supplier.trade or supplier.company,
            'cnpj': supplier.cnpj
        }
    
    # Buscar sugestões de materiais
    materials_suggestions = []
    for product in result.get('products', []):
        suggestions = []
        if supplier:
            similar = find_similar_materials(product.get('description', ''), supplier.id, limit=5)
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
            'product': product,
            'suggestions': suggestions,
            'selected_material': None
        })
    
    # Montar resultado final
    return {
        'photo_url': _get_image_url(job.image_path),
        'photo_public_id': job.image_path,
        'number': result.get('number', ''),
        'series': result.get('series', ''),
        'access_key': result.get('access_key', ''),
        'issue_date': result.get('issue_date', ''),
        'total_value': result.get('total_value', 0),
        'supplier': supplier_data,
        'supplier_name_detected': result.get('supplier_name', ''),
        'supplier_cnpj_detected': supplier_cnpj,
        'materials': materials_suggestions,
        'observations': result.get('observations', ''),
        'confidence': 1.0,
    }


def _process_ocr_job_locally(job: OCRJob) -> dict:
    """
    Processa OCR localmente (para desenvolvimento sem Supabase).
    """
    from fiscal.services.ocr import InvoiceOCRService
    from fiscal.models import Invoice
    
    try:
        image_bytes = _get_image_bytes(job.image_path)
        
        if not image_bytes:
            return {'success': False, 'error': 'Não foi possível carregar a imagem'}
        
        ocr_service = InvoiceOCRService()
        extracted = ocr_service.extract_from_bytes(image_bytes, mime_type='image/jpeg')
        
        if extracted.error:
            if '429' in extracted.error or 'quota' in extracted.error.lower():
                return {
                    'success': False,
                    'error': 'Limite diário de OCR atingido. Cadastre manualmente.',
                    'error_type': 'quota_exceeded'
                }
            return {'success': False, 'error': extracted.error}
        
        # Verificar duplicidade
        existing = Invoice.objects.filter(
            number=extracted.number,
            supplier__cnpj__icontains=extracted.supplier_cnpj[:8] if extracted.supplier_cnpj else ''
        ).first()
        
        if existing:
            return {
                'success': False,
                'error': f'Nota {extracted.number} já cadastrada para este fornecedor'
            }
        
        # Montar resultado
        return {
            'success': True,
            'data': {
                'number': extracted.number,
                'series': extracted.series,
                'access_key': extracted.access_key,
                'issue_date': extracted.issue_date,
                'supplier_name': extracted.supplier_name,
                'supplier_cnpj': extracted.supplier_cnpj,
                'total_value': extracted.total_value,
                'observations': extracted.observations,
                'products': [
                    {
                        'code': p.code,
                        'description': p.description,
                        'quantity': p.quantity,
                        'unit': p.unit,
                        'unit_price': p.unit_price,
                        'total_price': p.total_price,
                    }
                    for p in extracted.products
                ],
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def _get_image_bytes(image_path: str) -> bytes | None:
    """Recupera bytes da imagem a partir do path."""
    
    try:
        if image_path.startswith('local/'):
            from pathlib import Path
            relative_path = image_path.replace('local/', '')
            file_path = settings.MEDIA_ROOT / relative_path
            
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    return f.read()
            return None
        else:
            # Supabase Storage - bucket privado, usar API autenticada
            conf = _get_supabase_config()
            url = f"{conf['url']}/storage/v1/object/ocr-images/{image_path}"
            
            response = requests.get(
                url,
                headers={
                    'Authorization': f"Bearer {conf['service_key']}",
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Erro ao baixar imagem do Storage: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"Erro ao recuperar imagem: {e}")
        return None


def _get_image_url(image_path: str) -> str:
    """Retorna URL da imagem (para bucket privado, gera URL assinada)."""
    if image_path.startswith('local/'):
        relative_path = image_path.replace('local/', '')
        return f"{settings.MEDIA_URL}{relative_path}"
    else:
        # Para bucket privado, gerar URL assinada
        conf = _get_supabase_config()
        
        # Criar URL assinada válida por 1 hora
        try:
            response = requests.post(
                f"{conf['url']}/storage/v1/object/sign/ocr-images/{image_path}",
                headers={
                    'Authorization': f"Bearer {conf['service_key']}",
                    'Content-Type': 'application/json',
                },
                json={'expiresIn': 3600},  # 1 hora
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return f"{conf['url']}/storage/v1{data.get('signedURL', '')}"
        except Exception as e:
            print(f"Erro ao gerar URL assinada: {e}")
        
        # Fallback: retorna URL direta (só funciona se bucket for público)
        return f"{conf['url']}/storage/v1/object/ocr-images/{image_path}"


@login_required(login_url='authenticate:login')
def ocr_cancel(request, job_id):
    """
    Cancela um OCRJob e limpa a imagem do Storage.
    Chamado quando usuário sai da página sem salvar a nota.
    
    POST /fiscal/ocr/cancel/<job_id>/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        job = OCRJob.objects.get(id=job_id)
        
        # Deletar imagem do Storage
        from fiscal.services.storage import delete_image_from_storage
        if job.image_path:
            delete_image_from_storage(job.image_path)
        
        # Deletar o job
        job.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'OCRJob cancelado e imagem removida'
        })
        
    except OCRJob.DoesNotExist:
        return JsonResponse({
            'success': True,
            'message': 'Job já não existe'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
