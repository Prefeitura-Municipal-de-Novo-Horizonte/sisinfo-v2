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
