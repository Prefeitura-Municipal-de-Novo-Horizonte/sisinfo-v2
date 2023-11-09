from django.contrib import messages
from django.contrib.messages import constants
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import resolve_url as r
from django.urls import reverse

from dashboard.filters import DirectionFilter, SectorFilter
from dashboard.forms import DirectionForm, SectorForm
from dashboard.models import Direction, Sector


# Create your views here.
def index(request):
    context = {}
    return render(request, 'index.html', context)

##############################################
########## DIRETORIAS DASHBOARD ##############
##############################################

# DIRETORIA
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

    myFilter = DirectionFilter(request.GET, queryset=diretorias)
    diretorias = myFilter.qs
        
    context = {
        'form': form, 
        'diretorias': diretorias,
        'myFilter': myFilter,
        }
    return render(request, 'setores/diretorias.html', context)

def direction_detail(request, slug):
    diretoria = get_object_or_404(Direction, slug=slug)
    setores = Sector.objects.filter(direction=diretoria.id)
    context = {
        'diretoria': diretoria,
        'setores': setores,
    }
    return render(request, 'setores/diretoria_detail.html', context)

def direction_edit(request, slug, id):
    pass

def direction_delete(request, id):
    diretoria = get_object_or_404(Direction, id=id)
    diretoria.delete()
    messages.add_message(request, constants.ERROR, f'Diretoria {diretoria.name} foi excluida com sucesso!')
    return redirect(reverse('dashboard:diretorias'))

# SETOR
def sectors(request):
    setores = Sector.objects.all()
    if request.method == 'POST':
        form = SectorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, constants.SUCCESS, 'Inserido com sucesso!')
        else:
            messages.add_message(request, constants.ERROR, 'Ocorreu um erro!')
        return redirect(reverse('dashboard:setores'))
    form = SectorForm()

    myFilter = SectorFilter(request.GET, queryset=setores)
    setores = myFilter.qs

    context = {
        'form': form,
        'setores': setores,
        'myFilter': myFilter,
        }
    return render(request, 'setores/setores.html', context)

def sector_delete(request, id, slug):
    setor = get_object_or_404(Sector, id=id, slug=slug)
    setor.delete()
    messages.add_message(request, constants.ERROR, f'O Setor {setor.name} foi excluido com sucesso!')
    return redirect(reverse('dashboard:setores'))