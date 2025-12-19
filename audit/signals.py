"""
Signals para auditoria automática de operações CRUD.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from audit.services import AuditService
from threading import local
import logging

logger = logging.getLogger(__name__)

# Thread-local storage para armazenar request atual
_thread_locals = local()


def get_current_request():
    """Retorna request atual do thread-local"""
    return getattr(_thread_locals, 'request', None)


def set_current_request(request):
    """Armazena request no thread-local"""
    _thread_locals.request = request


# Lista de modelos a auditar (TODOS os modelos do sistema)
AUDITED_MODELS = [
    # Autenticação
    'ProfessionalUser',
    
    # Licitações e Fornecedores
    'Bidding',
    'Supplier',
    'Contact',
    'Material',
    'BiddingMaterial',
    'MaterialBidding',
    
    # Estrutura Organizacional
    'Department',
    'Position',
    'Employee',
    'Direction',
    'Sector',
    
    # Relatórios
    'Report',
    'Invoice',
    'InterestRequestMaterial',
    'MaterialReport',
    
    # Adicionar novos modelos aqui conforme necessário
]


@receiver(pre_save)
def capture_old_values(sender, instance, **kwargs):
    """
    Captura valores antigos antes de salvar para comparação.
    Executado antes de post_save.
    """
    # Skip durante loaddata
    if kwargs.get('raw', False):
        return
    
    if sender.__name__ not in AUDITED_MODELS:
        return
    
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_values = {}
            for field in instance._meta.fields:
                instance._old_values[field.name] = getattr(old_instance, field.name, None)
        except sender.DoesNotExist:
            instance._old_values = {}
    else:
        instance._old_values = {}


@receiver(post_save)
def log_create_update(sender, instance, created, **kwargs):
    """
    Registra criação ou atualização de registros.
    """
    # Skip durante loaddata
    if kwargs.get('raw', False):
        return
    
    if sender.__name__ not in AUDITED_MODELS:
        return
    
    request = get_current_request()
    user = request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None
    
    action = 'create' if created else 'update'
    changes = {}
    
    # Se foi atualização, captura as mudanças
    if not created and hasattr(instance, '_old_values'):
        for field_name, old_value in instance._old_values.items():
            new_value = getattr(instance, field_name, None)
            
            # Ignora campos internos e timestamps automáticos
            if field_name.startswith('_') or field_name in ['created_at', 'updated_at']:
                continue
            
            # Converte para string para comparação
            old_str = str(old_value) if old_value is not None else None
            new_str = str(new_value) if new_value is not None else None
            
            if old_str != new_str:
                changes[field_name] = {
                    'old': old_str,
                    'new': new_str
                }
    
    # Registra log
    AuditService.log_event(
        event_type='crud',
        user=user,
        model_name=sender.__name__,
        object_id=instance.pk,
        action=action,
        changes=changes if changes else None,
        request=request
    )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """
    Registra exclusão de registros.
    """
    if sender.__name__ not in AUDITED_MODELS:
        return
    
    request = get_current_request()
    user = request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None
    
    # Registra log com representação do objeto deletado
    AuditService.log_event(
        event_type='crud',
        user=user,
        model_name=sender.__name__,
        object_id=instance.pk,
        action='delete',
        request=request,
        metadata={'deleted_object': str(instance)}
    )
