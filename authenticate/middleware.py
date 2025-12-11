"""
Middleware para forçar onboarding em primeiro login.
"""
from django.shortcuts import redirect
from django.urls import reverse
from authenticate.models import ProfessionalUser


class OnboardingMiddleware:
    """
    Middleware que força usuários com first_login=True a completar o onboarding.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lista de URLs que são permitidas mesmo com first_login=True
        allowed_paths = [
            reverse('authenticate:onboarding'),
            reverse('authenticate:logout'),
            '/static/',
            '/media/',
        ]

        # Verifica se o usuário está autenticado
        if request.user.is_authenticated:
            # Verifica se é um ProfessionalUser com first_login=True
            if isinstance(request.user, ProfessionalUser) and request.user.first_login:
                # Verifica se a URL atual não está na lista de permitidas
                current_path = request.path
                is_allowed = any(current_path.startswith(path) for path in allowed_paths)

                if not is_allowed:
                    # Redireciona para onboarding
                    return redirect('authenticate:onboarding')

        response = self.get_response(request)
        return response
