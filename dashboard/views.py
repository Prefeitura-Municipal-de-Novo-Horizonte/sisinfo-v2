from django.contrib import messages
from django.contrib.messages import constants
from django.shortcuts import redirect, render
from django.shortcuts import resolve_url as r
from django.urls import reverse

from dashboard.forms import DirectionForm, SectorForm
from dashboard.models import Direction, Sector


# Create your views here.
def index(request):
    context = {}
    return render(request, 'index.html', context)

##############################################
########## DIRETORIAS DASHBOARD ##############
##############################################

def directions(request):
    diretorias = Direction.objects.all()
    if request.method == 'POST':
        form = DirectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, constants.SUCCESS,
                                 'Inserido com sucesso!')
        else:
            messages.add_message(request, constants.ERROR, 'Ocorreu um erro!')
        return redirect(reverse('dashboard:diretorias'))
    form = DirectionForm()
    context = {
        'form': form, 
        'diretorias': diretorias,
        }
    return render(request, 'setores/diretorias.html', context)

def sectors(request):
    setores = Sector.objects.all()
    if request.method == 'POST':
        form = SectorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, constants.SUCCESS,
                                 'Inserido com sucesso!')
        else:
            messages.add_message(request, constants.ERROR, 'Ocorreu um erro!')
        return redirect(reverse('dashboard:setores'))
    form = SectorForm()
    context = {
        'form': form,
        'setores': setores
        }
    return render(request, 'setores/setores.html', context)
