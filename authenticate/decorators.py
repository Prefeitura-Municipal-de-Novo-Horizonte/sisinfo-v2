from django.contrib import messages
from django.contrib.messages import constants
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Importação local para evitar circular import
            from authenticate.models import ProfessionalUser
            
            # Se usuário está no primeiro login, redireciona para onboarding
            if isinstance(request.user, ProfessionalUser) and request.user.first_login:
                return redirect('authenticate:onboarding')
            
            # Caso contrário, redireciona para dashboard
            return redirect('dashboard:index')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def admin_only(view_func):
    """
    Decorator que permite acesso apenas para administradores ativos.
    Usa o método can_access_admin() do modelo.
    """
    def wrapper_function(request, *args, **kwargs):
        if not hasattr(request.user, 'can_access_admin') or not request.user.can_access_admin():
            messages.add_message(request, constants.ERROR,
                                 'Você não tem autorização de administrador.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)

    return wrapper_function


def tech_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        if not request.user.is_tech:
            messages.add_message(request, constants.ERROR,
                                 'Você não tem autorização de Tecnico.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)

    return wrapper_function
