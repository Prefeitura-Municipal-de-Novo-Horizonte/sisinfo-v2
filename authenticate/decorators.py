from django.contrib import messages
from django.contrib.messages import constants
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        if request.user.is_admin != True:
            messages.add_message(request, constants.ERROR,
                                 'Você não tem autorização de administrador.')
            return redirect('dashboard:index')

        if request.user.is_admin == True:
            return view_func(request, *args, **kwargs)

    return wrapper_function


def tech_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        if request.user.is_tech != True:
            messages.add_message(request, constants.ERROR,
                                 'Você não tem autorização de Tecnico.')
            return redirect('dashboard:index')

        if request.user.is_tech == True:
            return view_func(request, *args, **kwargs)

    return wrapper_function
