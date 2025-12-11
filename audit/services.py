"""
Serviço de auditoria para registrar eventos no MongoDB.
"""
from datetime import datetime
from audit.mongodb import MongoDBConnection
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """
    Serviço para registrar eventos de auditoria no MongoDB.
    """
    
    @staticmethod
    def log_event(
        event_type,
        user,
        model_name,
        object_id,
        action,
        changes=None,
        request=None,
        metadata=None
    ):
        """
        Registra evento de auditoria no MongoDB.
        
        Args:
            event_type (str): Tipo do evento ('auth', 'crud', 'view')
            user: Objeto User ou None
            model_name (str): Nome do modelo afetado
            object_id: ID do objeto afetado
            action (str): Ação realizada ('create', 'update', 'delete', 'login', etc)
            changes (dict): Dicionário com mudanças (antes/depois)
            request: HttpRequest object
            metadata (dict): Dados adicionais
        """
        try:
            mongo = MongoDBConnection()
            if not mongo.logs:
                logger.warning("MongoDB não disponível, log não registrado")
                return
            
            # Monta documento de log
            log_entry = {
                'event_type': event_type,
                'action': action,
                'timestamp': datetime.utcnow(),
                'user_id': user.id if user and hasattr(user, 'id') else None,
                'username': getattr(user, 'username', None) if user else None,
                'email': getattr(user, 'email', None) if user else None,
                'model': model_name,
                'object_id': str(object_id) if object_id else None,
                'changes': changes or {},
                'metadata': metadata or {}
            }
            
            # Adiciona dados da requisição se disponível
            if request:
                log_entry.update({
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT'),
                    'path': request.path,
                    'method': request.method
                })
            
            # Insere no MongoDB
            mongo.logs.insert_one(log_entry)
            logger.debug(f"Audit log criado: {action} em {model_name} (ID: {object_id})")
            
        except Exception as e:
            logger.error(f"Erro ao criar audit log: {e}")
