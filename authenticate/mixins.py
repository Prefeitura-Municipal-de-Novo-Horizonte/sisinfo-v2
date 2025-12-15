"""
Mixins para controle de acesso em views.
"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages import constants


class TechOnlyMixin(UserPassesTestMixin):
    """
    Mixin que permite acesso apenas para usuários técnicos.
    Redireciona para a página anterior com mensagem de erro se não for técnico.
    """
    
    def test_func(self):
        """Testa se o usuário é técnico."""
        return self.request.user.is_authenticated and self.request.user.is_tech
    
    def handle_no_permission(self):
        """Adiciona mensagem de erro e redireciona."""
        messages.add_message(
            self.request,
            constants.ERROR,
            "Você não tem permissão para acessar esta página!"
        )
        return redirect(self.request.META.get('HTTP_REFERER', '/'))
