from django.contrib.auth import authenticate, login, logout
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
    if request.method != 'POST':
        return render(request, 'login.html', context={})
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)

    if user is None:
        # TODO: Adicionar mensagem de erro para ir a pagina de login
        return HttpResponse('Usuario não existe')
    login(request, user)
    if user.first_login is True:
        form = UserCreationForm(instance=user)
        context = {
            'form': form,
        }
        return render(request, 'change_password.html', context)
    return redirect('dashboard:index')


def change_password(request, slug):
    user_request = request.user
    user_verification = get_object_or_404(ProfessionalUser, slug=slug)
    if user_request == user_verification:
        user = user_request
        if request.method == 'GET':
            user_form = UserCreationForm(instance=user)
            context = {
                'form': user_form,
            }
            return render(request, 'change_password.html', context)
        elif request.method == 'POST':
            user_form = UserCreationForm(request.POST, instance=user)
            if user_form.is_valid():
                return user_extract_forms(user_form, user, slug)
    return redirect('authenticated:login')


def user_extract_forms(user_form, user, slug):
    user_form_get = user_form.save(commit=False)
    user_form_get.first_name = user_form.cleaned_data['first_name']
    user_form_get.last_name = user_form.cleaned_data['last_name']
    user_form_get.username = user_form.cleaned_data['username']
    user_form_get.email = user_form.cleaned_data['email']
    user_form_get.password1 = user_form.cleaned_data['password1']
    user_form_get.password2 = user_form.cleaned_data['password2']

    if user_form_get.password1 != user.password:
        user_form_get.save()
        user_altered = get_object_or_404(
            ProfessionalUser, slug=slug)
        user_altered.first_login = False
        user_altered.save()
        return redirect('blog:index')
    return redirect(reverse('authenticated:change_password', kwargs={'slug': slug}))


def logout_page(request):
    logout(request)
    return redirect('authenticated:login')
