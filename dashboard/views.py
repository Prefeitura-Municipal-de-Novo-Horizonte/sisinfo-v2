import json
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from decouple import config

from dashboard.services import DashboardService


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
    Verifica status da API Node.js OCR.
    Retorna JSON com status de todas as APIs.
    """
    vercel_url = config('VERCEL_URL', default='http://localhost:3000')
    
    # Construir URL da API health
    if vercel_url.startswith('http'):
        health_url = f"{vercel_url}/api/health"
    else:
        health_url = f"https://{vercel_url}/api/health"
    
    result = {
        'nodejs_api': {
            'url': health_url,
            'status': 'unknown',
            'message': '',
            'response_time_ms': None
        },
        'environment': {
            'vercel_url': vercel_url,
            'use_nodejs_ocr': config('USE_NODEJS_OCR', default='false'),
            'gemini_configured': bool(config('GEMINI_API_KEY', default=None)),
            'internal_secret_configured': bool(config('INTERNAL_API_SECRET', default=None))
        }
    }
    
    try:
        import time
        start = time.time()
        response = requests.get(health_url, timeout=5)
        elapsed = int((time.time() - start) * 1000)
        
        result['nodejs_api']['response_time_ms'] = elapsed
        
        if response.status_code == 200:
            data = response.json()
            result['nodejs_api']['status'] = data.get('status', 'ok')
            result['nodejs_api']['message'] = 'API respondendo normalmente'
            result['nodejs_api']['details'] = data.get('checks', {})
        else:
            result['nodejs_api']['status'] = 'error'
            result['nodejs_api']['message'] = f'Status code: {response.status_code}'
    except requests.Timeout:
        result['nodejs_api']['status'] = 'timeout'
        result['nodejs_api']['message'] = 'API não respondeu em 5s'
    except requests.RequestException as e:
        result['nodejs_api']['status'] = 'error'
        result['nodejs_api']['message'] = str(e)
    except Exception as e:
        result['nodejs_api']['status'] = 'error'
        result['nodejs_api']['message'] = f'Erro: {str(e)}'
    
    return JsonResponse(result)
