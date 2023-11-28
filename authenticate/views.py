from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from authenticate.decorators import admin_only, tech_only, unauthenticated_user
from authenticate.forms import (
    AuthenticationFormCustom,
    PasswordChangeCustomForm,
    UserChangeForm,
    UserCreationForm,
)
from authenticate.models import ProfessionalUser


@login_required(login_url='authenticated:login')
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
        return redirect(reverse('authenticated:login'))


@login_required(login_url='authenticated:login')
def change_password(request, slug):  # sourcery skip: extract-method
    if request.method == 'POST':
        user = request.user
        form = PasswordChangeCustomForm(user, data=request.POST)
        if form.is_valid():
            form.save()
            user_a = get_object_or_404(ProfessionalUser, slug=slug)
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
        return redirect(reverse('authenticated:change_password', kwargs={'slug': user.slug}))
    form = PasswordChangeCustomForm(request.user)
    context = {
        'form': form,
    }
    return render(request, 'change_password.html', context)


@login_required(login_url='authenticated:login')
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
            print(request.FILES)
            if form.is_valid():
                # TODO: Inserir upload de imagem
                print('OK')
                form.save()
                messages.add_message(
                    request, constants.SUCCESS, "Alterado com sucesso!")
                return redirect('authenticated:profile')
            messages.add_message(
                request, constants.ERROR, "Ocorreu um erro!")
            return redirect('authenticated:profile')
    return redirect('authenticated:login')


def logout_page(request):
    logout(request)
    messages.add_message(
        request, constants.SUCCESS, "Logout com sucesso!")
    return redirect('authenticated:login')


################################################################
################# Administration Users #########################
################################################################

@login_required(login_url='authenticated:login')
@admin_only
def register_user(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.add_message(
                request, constants.SUCCESS, f"Usuario adicionado com sucesso: {user}")
            return redirect('authenticated:register_user')
        messages.add_message(
            request, constants.ERROR, "Ocorreu um erro!")
    context = {
        'form': form,
    }
    return render(request, 'register_user.html', context)


# --- Deabilita e Habilita Usuário ---
@login_required(login_url='authenticated:login')
@admin_only
def disabled_user(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_active = False
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario desabilitado com sucesso: {user}")
    return redirect(reverse('authenticated:show_users'))


@login_required(login_url='authenticated:login')
@admin_only
def enabled_user(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_active = True
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario habilitado com sucesso: {user}")
    return redirect(reverse('authenticated:show_users'))


# --- Deabilita e Habilita Usuário Admin ---
@login_required(login_url='authenticated:login')
@admin_only
def enabled_user_admin(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    if user.is_tech is False:
        user.is_tech = True
    user.is_admin = True
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario habilitado como administrador com sucesso: {user}")
    return redirect(reverse('authenticated:show_users'))


@login_required(login_url='authenticated:login')
@admin_only
def disabled_user_admin(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_admin = False
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario desabilitador como administrador com sucesso: {user}")
    return redirect(reverse('authenticated:show_users'))


# --- Deabilita e Habilita Usuário Tech ---
@login_required(login_url='authenticated:login')
@admin_only
def enabled_user_tech(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_tech = True
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario habilitado como tecnico com sucesso: {user}")
    return redirect(reverse('authenticated:show_users'))


@login_required(login_url='authenticated:login')
@admin_only
def disabled_user_tech(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    if user.is_admin is True:
        user.is_admin = False
    user.is_tech = False
    user.save()
    messages.add_message(
        request, constants.SUCCESS, f"Usuario desabilitado como tecnico com sucesso: {user}")
    return redirect(reverse('authenticated:show_users'))


@login_required(login_url='authenticated:login')
@admin_only
def profile_user(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    print(user)
    context = {
        'user': user,
    }
    return render(request, 'profiles.html', context)
