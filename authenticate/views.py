from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.shortcuts import get_object_or_404, redirect, render

from authenticate.decorators import admin_only, unauthenticated_user
from authenticate.forms import (
    AuthenticationFormCustom,
    PasswordChangeCustomForm,
    UserChangeForm,
    UserCreationForm,
)
from authenticate.models import ProfessionalUser


@login_required
@admin_only
def show_users(request):
    users = ProfessionalUser.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'users.html', context)


################################################################
################### LOGIN AND LOGOUT ###########################
################################################################
@unauthenticated_user
def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    elif request.method == 'GET':
        form = AuthenticationFormCustom(request)
        context = {
            'form': form,
        }
        return render(request, 'login.html', context)
    elif request.method == 'POST':
        form = AuthenticationFormCustom(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.first_login is True:
                form = PasswordChangeCustomForm(request.user)
                context = {
                    'form': form
                }
                return render(request, 'change_password.html', context)
            return redirect('dashboard:index')
        messages.add_message(request, constants.ERROR,
                             "Usuário ou Senha inválidos!")
        return redirect('authenticate:login')


@login_required
def change_password(request):  # sourcery skip: extract-method
    if request.method == 'POST':
        user = request.user
        form = PasswordChangeCustomForm(user, data=request.POST)
        if form.is_valid():
            form.save()
            user_a = get_object_or_404(ProfessionalUser, slug=request.user.slug)
            if user.first_login is True:
                user_a.first_login = False
                user_a.save()
                messages.add_message(
                    request, constants.SUCCESS, "Senha trocada com sucesso!")
                return redirect('dashboard:index')
            messages.add_message(request, constants.SUCCESS,
                                 "Senha trocada com sucesso!")
            return redirect('dashboard:index')
        messages.add_message(request, constants.ERROR, "Ocorreu um erro!")
        return redirect('authenticate:change_password')
    form = PasswordChangeCustomForm(request.user)
    context = {
        'form': form,
    }
    return render(request, 'change_password.html', context)


@login_required
def alter_user(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            form = UserChangeForm(instance=request.user)
            context = {
                'form': form,
            }
            return render(request, 'profile_professional.html', context)
        if request.method == 'POST':
            form = UserChangeForm(request.POST, files=request.FILES,
                                  instance=request.user)
            if form.is_valid():
                form.save()
                messages.add_message(
                    request, constants.SUCCESS, "Alterado com sucesso!")
                return redirect('authenticate:profile')
            messages.add_message(
                request, constants.ERROR, "Ocorreu um erro!")
            return redirect('authenticate:profile')
    return redirect('authenticate:login')


def logout_page(request):
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
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.add_message(
                request, constants.SUCCESS, f"Usuario adicionado com sucesso: {user}")
            return redirect('authenticate:register_user')
        messages.add_message(
            request, constants.ERROR, "Ocorreu um erro!")
    context = {
        'form': form,
    }
    return render(request, 'register_user.html', context)


# --- Deabilita e Habilita Usuário ---
@login_required
@admin_only
def disabled_user(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_active = False
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario desabilitado com sucesso: {user}")
    return redirect('authenticate:show_users')


@login_required
@admin_only
def enabled_user(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_active = True
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario habilitado com sucesso: {user}")
    return redirect('authenticate:show_users')


# --- Deabilita e Habilita Usuário Admin ---
@login_required
@admin_only
def enabled_user_admin(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    if user.is_tech is False:
        user.is_tech = True
    user.is_admin = True
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario habilitado como administrador com sucesso: {user}")
    return redirect('authenticate:show_users')


@login_required
@admin_only
def disabled_user_admin(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_admin = False
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario desabilitador como administrador com sucesso: {user}")
    return redirect('authenticate:show_users')


# --- Deabilita e Habilita Usuário Tech ---
@login_required
@admin_only
def enabled_user_tech(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_tech = True
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario habilitado como tecnico com sucesso: {user}")
    return redirect('authenticate:show_users')


@login_required
@admin_only
def disabled_user_tech(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    if user.is_admin is True:
        user.is_admin = False
    user.is_tech = False
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario desabilitado como tecnico com sucesso: {user}")
    return redirect('authenticate:show_users')


@login_required
@admin_only
def profile_user(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    context = {
        'user': user,
    }
    return render(request, 'profiles.html', context)
