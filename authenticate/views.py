from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from authenticate.forms import UserCreationForm
from authenticate.models import ProfessionalUser


def show_users(request):
    users = ProfessionalUser.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'users.html', context)


################################################################
################### LOGIN AND LOGOUT ###########################
################################################################
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


def logout_page(request):
    logout(request)
    # TODO: Adicionar mensagem de SUCCESS
    return redirect('authenticated:login')


# --- Deabilita e Habilita Usuário ---
def disabled_user(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_active = False
    user.save()
    return redirect(reverse('authenticated:show_users'))


def enabled_user(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_active = True
    user.save()
    return redirect(reverse('authenticated:show_users'))


# --- Deabilita e Habilita Usuário Admin ---
def enabled_user_admin(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    if user.is_tech is False:
        user.is_tech = True
    user.is_admin = True
    user.save()
    return redirect(reverse('authenticated:show_users'))


def disabled_user_admin(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_admin = False
    user.save()
    return redirect(reverse('authenticated:show_users'))


# --- Deabilita e Habilita Usuário Tech ---
def enabled_user_tech(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    user.is_tech = True
    user.save()
    return redirect(reverse('authenticated:show_users'))


def disabled_user_tech(request, slug):
    user = get_object_or_404(ProfessionalUser, slug=slug)
    if user.is_admin is True:
        user.is_admin = False
    user.is_tech = False
    user.save()
    return redirect(reverse('authenticated:show_users'))
