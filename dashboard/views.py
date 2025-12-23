import json
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from decouple import config

from dashboard.services import DashboardService


@login_required
def admin_panel(request):
    """
    Página de administração com ferramentas de manutenção.
    Restrito a administradores.
    """
    if not request.user.is_admin:
        from django.shortcuts import redirect
        return redirect('dashboard:index')
    
    return render(request, "dashboard/admin.html")


@login_required
def index(request):
    """
    View principal do Dashboard.
    """
    # Estatísticas para cards
    stats = DashboardService.get_dashboard_data(request.user)
    
    # Initial data for main chart (30 days)
    sector_data = DashboardService.get_reports_by_sector(30)

    # Top Materials
    materials_data = DashboardService.get_top_materials_by_period(30)

    # Calendar Events
    calendar_events = DashboardService.get_recent_reports_for_calendar()

    context = {
        # Stats for cards
        **stats,
        
        # Main Chart Data (passed to partial logic or initial render)
        'sector_labels': json.dumps([item['sector__name'] for item in sector_data]),
        'sector_series': json.dumps([item['count'] for item in sector_data]),

        # Materials Chart
        'material_labels': json.dumps([item['name'] for item in materials_data]),
        'material_series': json.dumps([str(item['qty']) for item in materials_data]), # Decimal to str

        # Calendar
        'calendar_events': json.dumps(calendar_events),
    }
    return render(request, "index.html", context)


@login_required
def reports_by_sector_chart(request):
    """
    Retorna o gráfico atualizado via HTMX.
    """
    try:
        days = int(request.GET.get('days', 30))
    except ValueError:
        days = 30

    sector_data = DashboardService.get_reports_by_sector(days)

    labels = json.dumps([item['sector__name'] for item in sector_data])
    series = json.dumps([item['count'] for item in sector_data])

    # Retornamos apenas o script de atualização do gráfico ou o partial
    # Para simplicidade com HTMX, vamos retornar um partial com o gráfico recriado
    context = {
        'sector_labels': labels,
        'sector_series': series,
    }
    return render(request, "dashboard/partials/sector_chart.html", context)


@login_required
def top_materials_chart(request):
    """
    Retorna dados dos materiais mais utilizados por período via HTMX.
    """
    try:
        days = int(request.GET.get('days', 30))
    except ValueError:
        days = 30

    materials_data = DashboardService.get_top_materials_by_period(days)

    labels = json.dumps([item['name'] for item in materials_data])
    series = json.dumps([str(item['qty']) for item in materials_data])

    context = {
        'material_labels': labels,
        'material_series': series,
    }
    return render(request, "dashboard/partials/materials_chart.html", context)


@login_required
def api_status(request):
    """
    Verifica status dos serviços externos.
    Retorna JSON com status do Supabase Edge Functions.
    """
    supabase_url = config('SUPABASE_URL', default='')
    
    result = {
        'supabase': {
            'url': supabase_url,
            'status': 'unknown',
            'message': '',
            'response_time_ms': None
        },
        'environment': {
            'supabase_configured': bool(supabase_url),
            'gemini_configured': bool(config('GEMINI_API_KEY', default=None)),
        }
    }
    
    if not supabase_url:
        result['supabase']['status'] = 'not_configured'
        result['supabase']['message'] = 'Supabase não configurado'
        return JsonResponse(result)
    
    try:
        import time
        start = time.time()
        # Verificar se Supabase está acessível
        health_url = f"{supabase_url}/rest/v1/"
        response = requests.get(
            health_url, 
            headers={'apikey': config('SUPABASE_ANON_KEY', default='')},
            timeout=5
        )
        elapsed = int((time.time() - start) * 1000)
        
        result['supabase']['response_time_ms'] = elapsed
        
        if response.status_code in [200, 401]:  # 401 é ok, significa que está respondendo
            result['supabase']['status'] = 'ok'
            result['supabase']['message'] = 'Supabase respondendo normalmente'
        else:
            result['supabase']['status'] = 'error'
            result['supabase']['message'] = f'Status code: {response.status_code}'
    except requests.Timeout:
        result['supabase']['status'] = 'timeout'
        result['supabase']['message'] = 'Supabase não respondeu em 5s'
    except requests.RequestException as e:
        result['supabase']['status'] = 'error'
        result['supabase']['message'] = str(e)
    except Exception as e:
        result['supabase']['status'] = 'error'
        result['supabase']['message'] = f'Erro: {str(e)}'
    
    return JsonResponse(result)


@login_required
def clean_ocr_jobs(request):
    """
    Limpa TODOS os OCRJobs e imagens órfãs do Storage.
    Restrito a administradores.
    Retorna JSON com resultado da limpeza.
    """
    from fiscal.models import OCRJob, Invoice
    from fiscal.services.storage import delete_image_from_storage, _get_supabase_config
    import requests
    
    # Verificar se é admin
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Apenas administradores podem executar esta ação'
        }, status=403)
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método não permitido'
        }, status=405)
    
    try:
        # 1. Limpar todos os OCRJobs
        total_jobs = OCRJob.objects.count()
        OCRJob.objects.all().delete()
        
        # 2. Limpar imagens órfãs do Storage
        orphan_deleted = 0
        conf = _get_supabase_config()
        
        if conf['url'] and conf['service_key']:
            # Listar imagens no bucket
            try:
                url = f"{conf['url']}/storage/v1/object/list/ocr-images"
                response = requests.post(
                    url,
                    headers={
                        'Authorization': f"Bearer {conf['service_key']}",
                        'Content-Type': 'application/json',
                    },
                    json={'prefix': '', 'limit': 10000},
                    timeout=30
                )
                
                if response.status_code == 200:
                    storage_images = {item['name'] for item in response.json() if item.get('name')}
                    
                    # Imagens referenciadas no banco
                    invoice_photos = set(
                        Invoice.objects.exclude(photo__isnull=True)
                        .exclude(photo='')
                        .exclude(photo__startswith='local/')
                        .values_list('photo', flat=True)
                    )
                    
                    # Identificar órfãs
                    orphan_images = storage_images - invoice_photos
                    
                    # Deletar órfãs
                    for img in orphan_images:
                        if delete_image_from_storage(img):
                            orphan_deleted += 1
            except Exception as e:
                print(f"Erro ao limpar imagens órfãs: {e}")
        
        return JsonResponse({
            'success': True,
            'deleted': total_jobs,
            'orphan_images_deleted': orphan_deleted,
            'message': f'{total_jobs} jobs removidos e {orphan_deleted} imagens órfãs deletadas!'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def backup_database(request):
    """
    Gera backup do banco de dados usando dumpdata do Django.
    Retorna arquivo JSON para download.
    Restrito a administradores.
    """
    from io import StringIO
    from django.core.management import call_command
    from django.utils import timezone
    
    # Verificar se é admin
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Apenas administradores podem executar esta ação'
        }, status=403)
    
    try:
        # Criar buffer para capturar o output
        output = StringIO()
        
        # Apps para fazer backup (exclui apps do Django e de terceiros)
        apps_to_backup = [
            'authenticate',
            'organizational_structure',
            'bidding_procurement',
            'bidding_supplier',
            'reports',
            'fiscal',
        ]
        
        # Executar dumpdata
        call_command(
            'dumpdata',
            *apps_to_backup,
            indent=2,
            stdout=output,
            exclude=['contenttypes', 'auth.permission', 'sessions'],
        )
        
        # Preparar resposta para download
        backup_content = output.getvalue()
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'sisinfo_backup_{timestamp}.json'
        
        response = HttpResponse(backup_content, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(backup_content.encode('utf-8'))
        
        return response
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def backup_start(request):
    """
    Inicia um job de backup assíncrono.
    Retorna o ID do job para polling.
    """
    from dashboard.models import BackupJob
    
    # Verificar se é admin
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Apenas administradores podem executar esta ação'
        }, status=403)
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método não permitido'
        }, status=405)
    
    try:
        # Criar job pendente
        job = BackupJob.objects.create(status='pending')
        
        return JsonResponse({
            'success': True,
            'job_id': str(job.id),
            'message': 'Job de backup criado. Use /manutencao/backup/status/<job_id>/ para verificar.'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def backup_process(request, job_id):
    """
    Processa um job de backup pendente.
    Chamado via polling pelo frontend.
    """
    from io import StringIO
    from django.core.management import call_command
    from dashboard.models import BackupJob
    
    # Verificar se é admin
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Apenas administradores podem executar esta ação'
        }, status=403)
    
    try:
        job = BackupJob.objects.get(id=job_id)
    except BackupJob.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Job não encontrado'
        }, status=404)
    
    # Se já foi processado, retornar status atual
    if job.status in ['completed', 'failed']:
        return JsonResponse({
            'success': True,
            'status': job.status,
            'message': 'Job já processado'
        })
    
    # Se está pending, processar agora
    if job.status == 'pending':
        job.mark_processing()
        
        try:
            output = StringIO()
            
            apps_to_backup = [
                'authenticate',
                'organizational_structure',
                'bidding_procurement',
                'bidding_supplier',
                'reports',
                'fiscal',
            ]
            
            call_command(
                'dumpdata',
                *apps_to_backup,
                indent=2,
                stdout=output,
                exclude=['contenttypes', 'auth.permission', 'sessions'],
            )
            
            job.mark_completed(output.getvalue())
            
            return JsonResponse({
                'success': True,
                'status': 'completed',
                'message': 'Backup concluído com sucesso!'
            })
        
        except Exception as e:
            job.mark_failed(str(e))
            return JsonResponse({
                'success': False,
                'status': 'failed',
                'error': str(e)
            })
    
    return JsonResponse({
        'success': True,
        'status': job.status
    })


@login_required
def backup_status(request, job_id):
    """
    Verifica o status de um job de backup.
    """
    from dashboard.models import BackupJob
    
    # Verificar se é admin
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Apenas administradores podem executar esta ação'
        }, status=403)
    
    try:
        job = BackupJob.objects.get(id=job_id)
        return JsonResponse({
            'success': True,
            'status': job.status,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'has_result': bool(job.result),
            'error': job.error_message if job.status == 'failed' else None
        })
    except BackupJob.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Job não encontrado'
        }, status=404)


@login_required
def backup_download(request, job_id):
    """
    Faz download do backup de um job concluído.
    """
    from dashboard.models import BackupJob
    from django.utils import timezone
    
    # Verificar se é admin
    if not request.user.is_admin:
        return JsonResponse({
            'success': False,
            'error': 'Apenas administradores podem executar esta ação'
        }, status=403)
    
    try:
        job = BackupJob.objects.get(id=job_id)
        
        if job.status != 'completed':
            return JsonResponse({
                'success': False,
                'error': f'Job ainda não concluído. Status: {job.status}'
            }, status=400)
        
        if not job.result:
            return JsonResponse({
                'success': False,
                'error': 'Backup vazio ou não disponível'
            }, status=400)
        
        timestamp = job.completed_at.strftime('%Y%m%d_%H%M%S') if job.completed_at else timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'sisinfo_backup_{timestamp}.json'
        
        response = HttpResponse(job.result, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(job.result.encode('utf-8'))
        
        return response
    
    except BackupJob.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Job não encontrado'
        }, status=404)

