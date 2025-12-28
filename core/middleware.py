"""
Middlewares centralizados do projeto.
"""
from django.utils import timezone


class TimezoneMiddleware:
    """
    Middleware que define o timezone padrão para todas as requisições.
    Garante que todas as operações de data/hora usem o fuso horário de São Paulo.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Ativa timezone de São Paulo para a requisição
        timezone.activate('America/Sao_Paulo')
        
        response = self.get_response(request)
        
        # Desativa após processar (volta ao default)
        timezone.deactivate()
        
        return response
