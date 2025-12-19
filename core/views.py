"""
View para restaurar backup via URL protegida.
Apenas superusuários podem acessar.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from io import StringIO


@require_GET
@staff_member_required
def restore_backup_view(request):
    """
    Endpoint para restaurar backup.
    Acesse: /admin/restore-backup/?confirm=yes
    
    Apenas staff pode acessar.
    """
    confirm = request.GET.get('confirm', '')
    fixture = request.GET.get('fixture', 'initial_data.json')
    
    if confirm != 'yes':
        return JsonResponse({
            'status': 'pending',
            'message': 'Para confirmar a restauração, acesse com ?confirm=yes',
            'fixture': fixture,
            'warning': 'ATENÇÃO: Isso pode sobrescrever dados existentes!'
        })
    
    # Executar restore
    output = StringIO()
    try:
        call_command('restore_backup', fixture=fixture, stdout=output)
        return JsonResponse({
            'status': 'success',
            'message': 'Backup restaurado com sucesso!',
            'output': output.getvalue()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'output': output.getvalue()
        }, status=500)
