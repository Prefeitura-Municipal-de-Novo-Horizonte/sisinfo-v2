from typing import Optional
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from .models import ProfessionalUser
from .forms import UserCreationForm, UserChangeForm, PasswordChangeCustomForm


class AuthenticateService:
    """
    Serviço responsável pela lógica de negócios relacionada a Autenticação e Gestão de Usuários.
    """

    @staticmethod
    def get_all_users() -> QuerySet[ProfessionalUser]:
        """Retorna todos os usuários profissionais cadastrados."""
        return ProfessionalUser.objects.all()

    @staticmethod
    def get_user_by_slug(slug: str) -> ProfessionalUser:
        """Retorna um usuário específico pelo slug ou 404 se não encontrado."""
        return get_object_or_404(ProfessionalUser, slug=slug)

    @staticmethod
    def create_user(form: UserCreationForm) -> Optional[ProfessionalUser]:
        """
        Cria um novo usuário a partir de um formulário validado.

        Args:
            form (UserCreationForm): Formulário preenchido.

        Returns:
            ProfessionalUser: O usuário criado se sucesso, None caso contrário.
        """
        if form.is_valid():
            return form.save()
        return None

    @staticmethod
    def update_user_profile(user: ProfessionalUser, form: UserChangeForm) -> Optional[ProfessionalUser]:
        """
        Atualiza o perfil de um usuário.

        Args:
            user (ProfessionalUser): Usuário a ser atualizado.
            form (UserChangeForm): Formulário com novos dados.

        Returns:
            ProfessionalUser: O usuário atualizado se sucesso, None caso contrário.
        """
        if form.is_valid():
            return form.save()
        return None

    @staticmethod
    def change_password(form: PasswordChangeCustomForm) -> bool:
        """
        Altera a senha do usuário.

        Args:
            form (PasswordChangeCustomForm): Formulário de troca de senha.

        Returns:
            bool: True se sucesso, False caso contrário.
        """
        if form.is_valid():
            form.save()
            return True
        return False

    @staticmethod
    def update_first_login(user: ProfessionalUser) -> None:
        """Atualiza o flag de primeiro login para False."""
        if user.first_login:
            user.first_login = False
            user.save()

    @staticmethod
    def disable_user(user: ProfessionalUser) -> str:
        """Desabilita um usuário (is_active = False)."""
        user.is_active = False
        user.save()
        return f"Usuario desabilitado com sucesso: {user}"

    @staticmethod
    def enable_user(user: ProfessionalUser) -> str:
        """Habilita um usuário (is_active = True)."""
        user.is_active = True
        user.save()
        return f"Usuario habilitado com sucesso: {user}"

    @staticmethod
    def promote_to_admin(user: ProfessionalUser) -> str:
        """Promove usuário a Administrador (e Técnico)."""
        if not user.is_tech:
            user.is_tech = True
        user.is_admin = True
        user.save()
        return f"Usuario habilitado como administrador com sucesso: {user}"

    @staticmethod
    def demote_from_admin(user: ProfessionalUser) -> str:
        """Remove privilégios de Administrador."""
        user.is_admin = False
        user.save()
        return f"Usuario desabilitado como administrador com sucesso: {user}"

    @staticmethod
    def promote_to_tech(user: ProfessionalUser) -> str:
        """Promove usuário a Técnico."""
        user.is_tech = True
        user.save()
        return f"Usuario habilitado como tecnico com sucesso: {user}"

    @staticmethod
    def demote_from_tech(user: ProfessionalUser) -> str:
        """Remove privilégios de Técnico (e Administrador se houver)."""
        if user.is_admin:
            user.is_admin = False
        user.is_tech = False
        user.save()
        return f"Usuario desabilitado como tecnico com sucesso: {user}"
    
    @staticmethod
    def get_active_users() -> QuerySet[ProfessionalUser]:
        """Retorna apenas usuários ativos."""
        return ProfessionalUser.objects.filter(is_active=True)
    
    @staticmethod
    def get_admins() -> QuerySet[ProfessionalUser]:
        """Retorna apenas administradores ativos."""
        return ProfessionalUser.objects.filter(is_admin=True, is_active=True)
    
    @staticmethod
    def get_techs() -> QuerySet[ProfessionalUser]:
        """Retorna apenas técnicos ativos."""
        return ProfessionalUser.objects.filter(is_tech=True, is_active=True)
