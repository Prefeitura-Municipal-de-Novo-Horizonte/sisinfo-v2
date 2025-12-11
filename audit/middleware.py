"""
Middleware para capturar request e disponibilizar nos signals.
"""
from audit.signals import set_current_request


class AuditMiddleware:
    """
    Middleware que disponibiliza o request atual para os signals.
    Isso permite que os signals tenham acesso ao usuário e dados da requisição.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Armazena request no thread-local
        set_current_request(request)
        
        # Processa request
        response = self.get_response(request)
        
        # Limpa request do thread-local
        set_current_request(None)
        
        return response
