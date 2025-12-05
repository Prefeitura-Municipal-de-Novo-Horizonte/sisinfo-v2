from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.shortcuts import redirect, render

from authenticate.decorators import admin_only, unauthenticated_user
from authenticate.forms import (
    AuthenticationFormCustom,
    PasswordChangeCustomForm,
    UserChangeForm,
    UserCreationForm,
)
from authenticate.services import AuthenticateService


@login_required
@admin_only
def show_users(request):
    """
    View para listar todos os usuários (apenas admin).
    """
    users = AuthenticateService.get_all_users()
    context = {
        'users': users,
    }
    return render(request, 'users/users.html', context)


################################################################
################### LOGIN AND LOGOUT ###########################
################################################################
@unauthenticated_user
def login_page(request):
    """
    View para login de usuários.
    Redireciona para dashboard se já autenticado.
    Se primeiro login, redireciona para troca de senha.
    """
    if request.method == 'POST':
        form = AuthenticationFormCustom(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.first_login is True:
                form = PasswordChangeCustomForm(request.user)
                context = {
                    'form': form
                }
                return render(request, 'users/change_password.html', context)
            return redirect('dashboard:index')
        messages.add_message(request, constants.ERROR,
                             "Usuário ou Senha inválidos!")
        return render(request, 'auth/login.html', {'form': form})

    form = AuthenticationFormCustom(request)
    context = {
        'form': form,
    }
    return render(request, 'auth/login.html', context)


@login_required
def change_password(request):
    """
    View para troca de senha.
    Atualiza flag de primeiro login se necessário.
    """
    if request.method == 'POST':
        user = request.user
        form = PasswordChangeCustomForm(user, data=request.POST)
        if AuthenticateService.change_password(form):
            AuthenticateService.update_first_login(user)
            messages.add_message(request, constants.SUCCESS,
                                 "Senha trocada com sucesso!")
            return redirect('dashboard:index')
        messages.add_message(request, constants.ERROR, "Ocorreu um erro!")
        return redirect('authenticate:change_password')
    form = PasswordChangeCustomForm(request.user)
    context = {
        'form': form,
    }
    return render(request, 'users/change_password.html', context)


@login_required
def alter_user(request):
    """
    View para alteração de perfil do próprio usuário.
    """
    if request.user.is_authenticated:
        if request.method == 'GET':
            form = UserChangeForm(instance=request.user)
            context = {
                'form': form,
            }
            return render(request, 'users/profile_professional.html', context)
        if request.method == 'POST':
            form = UserChangeForm(request.POST, files=request.FILES,
                                  instance=request.user)
            if AuthenticateService.update_user_profile(request.user, form):
                messages.add_message(
                    request, constants.SUCCESS, "Alterado com sucesso!")
                return redirect('authenticate:profile')
            messages.add_message(
                request, constants.ERROR, "Ocorreu um erro!")
            return redirect('authenticate:profile')
    return redirect('authenticate:login')


def logout_page(request):
    """
    View para logout.
    """
    logout(request)
    messages.add_message(
        request, constants.SUCCESS, "Logout com sucesso!")
    return redirect('authenticate:login')


################################################################
################# Administration Users #########################
################################################################

@login_required
@admin_only
def register_user(request):
    """
    View para registro de novos usuários (apenas admin).
    """
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        user = AuthenticateService.create_user(form)
        if user:
            messages.add_message(
                request, constants.SUCCESS, f"Usuario adicionado com sucesso: {user}")
            return redirect('authenticate:register_user')
        messages.add_message(
            request, constants.ERROR, "Ocorreu um erro!")
    context = {
        'form': form,
    }
    return render(request, 'users/register_user.html', context)


# --- Deabilita e Habilita Usuário ---
@login_required
@admin_only
def disabled_user(request, slug):
    """Desabilita um usuário."""
    user = AuthenticateService.get_user_by_slug(slug)
    msg = AuthenticateService.disable_user(user)
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect('authenticate:show_users')


@login_required
@admin_only
def enabled_user(request, slug):
    """Habilita um usuário."""
    user = AuthenticateService.get_user_by_slug(slug)
    msg = AuthenticateService.enable_user(user)
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect('authenticate:show_users')


# --- Deabilita e Habilita Usuário Admin ---
@login_required
@admin_only
def enabled_user_admin(request, slug):
    """Promove usuário a Admin."""
    user = AuthenticateService.get_user_by_slug(slug)
    msg = AuthenticateService.promote_to_admin(user)
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect('authenticate:show_users')


@login_required
@admin_only
def disabled_user_admin(request, slug):
    """Remove privilégios de Admin."""
    user = AuthenticateService.get_user_by_slug(slug)
    msg = AuthenticateService.demote_from_admin(user)
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect('authenticate:show_users')


# --- Deabilita e Habilita Usuário Tech ---
@login_required
@admin_only
def enabled_user_tech(request, slug):
    """Promove usuário a Técnico."""
    user = AuthenticateService.get_user_by_slug(slug)
    msg = AuthenticateService.promote_to_tech(user)
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect('authenticate:show_users')


@login_required
@admin_only
def disabled_user_tech(request, slug):
    """Remove privilégios de Técnico."""
    user = AuthenticateService.get_user_by_slug(slug)
    msg = AuthenticateService.demote_from_tech(user)
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect('authenticate:show_users')


@login_required
@admin_only
def profile_user(request, slug):
    """Visualiza perfil de outro usuário (apenas admin)."""
    user = AuthenticateService.get_user_by_slug(slug)
    context = {
        'user': user,
    }
    return render(request, 'users/profile_professional.html', context)
