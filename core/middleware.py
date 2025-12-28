"""
Middlewares centralizados do projeto.
"""
from decouple import config
from django.shortcuts import render
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


class MaintenanceMiddleware:
    """
    Middleware para modo de manutenção.
    
    Quando MAINTENANCE_MODE=True no .env, exibe página de manutenção
    para todos os usuários exceto superusuários.
    
    Uso:
        1. Adicione MAINTENANCE_MODE=True ao .env
        2. O site mostrará templates/maintenance.html para visitantes
        3. Superusuários ainda podem acessar normalmente
        4. Remova ou defina MAINTENANCE_MODE=False para desativar
    
    Não precisa de deploy para ativar/desativar (se usando Vercel/Heroku,
    basta alterar variável de ambiente no painel).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verifica se modo manutenção está ativo
        maintenance_mode = config('MAINTENANCE_MODE', default=False, cast=bool)
        
        if maintenance_mode:
            # Permite acesso de superusuários
            if request.user.is_authenticated and request.user.is_superuser:
                return self.get_response(request)
            
            # Permite acesso à página de login (para admins entrarem)
            allowed_paths = ['/authenticate/login/', '/admin/']
            if any(request.path.startswith(path) for path in allowed_paths):
                return self.get_response(request)
            
            # Exibe página de manutenção
            return render(request, 'maintenance.html', status=503)
        
        return self.get_response(request)

