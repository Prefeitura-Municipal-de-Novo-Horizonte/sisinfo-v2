from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from authenticate.decorators import admin_only, tech_only, unauthenticated_user
from authenticate.forms import UserChangeForm, UserCreationForm
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
        form = AuthenticationForm(request)
        context = {
            'form': form,
        }
        return render(request, 'login.html', context)
    elif request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.first_login is True:
                form = PasswordChangeForm(request.user)
                context = {
                    'form': form
                }
                return render(request, 'change_password.html', context)
            # TODO: Adicionar mensagem de login SUCCESS
            return redirect('dashboard:index')
        return redirect(reverse('authenticated:login'))


@login_required(login_url='authenticated:login')
def change_password(request, slug):  # sourcery skip: extract-method
    if request.method == 'POST':
        user = request.user
        form = PasswordChangeForm(user, data=request.POST)
        if form.is_valid():
            form.save()
            user_a = get_object_or_404(ProfessionalUser, slug=slug)
            if user.first_login is True:
                user_a.first_login = False
                user_a.save()
                # TODO: Adicionar mensagem de SUCCESS
                return redirect('dashboard:index')
            # TODO: Adicionar mensagem de SUCCESS
            return redirect('dashboard:index')
        # TODO: Adicionar mensagem de ERROR
        return redirect(reverse('authenticated:change_password', kwargs={'slug': user.slug}))
    form = PasswordChangeForm(request.user)
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
                return redirect('authenticated:profile')
    return redirect('authenticated:login')


def logout_page(request):
    logout(request)
    # TODO: Adicionar mensagem de SUCCESS
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
            # TODO: Adicionar mensagem de SUCCESS
            print(f'Usuario adicionado com sucesso: {user}')
            return redirect('authenticated:register_user')
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
    return redirect(reverse('authenticated:show_users'))


@login_required(login_url='authenticated:login')
@admin_only
def enabled_user(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_active = True
    user.save()
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
    return redirect(reverse('authenticated:show_users'))


@login_required(login_url='authenticated:login')
@admin_only
def disabled_user_admin(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_admin = False
    user.save()
    return redirect(reverse('authenticated:show_users'))


# --- Deabilita e Habilita Usuário Tech ---
@login_required(login_url='authenticated:login')
@admin_only
def enabled_user_tech(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_tech = True
    user.save()
    return redirect(reverse('authenticated:show_users'))


@login_required(login_url='authenticated:login')
@admin_only
def disabled_user_tech(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    if user.is_admin is True:
        user.is_admin = False
    user.is_tech = False
    user.save()
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
