from django.contrib import messages
from django.contrib.messages import constants
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
            messages.add_message(request, constants.SUCCESS, 'Inserido com sucesso!')
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
        'btn': 'Adicionar nova Diretoria'
        }
    return render(request, 'setores/diretorias.html', context)

def direction_detail(request, slug):
    diretoria = get_object_or_404(Direction, slug=slug)
    setores = Sector.objects.filter(direction=diretoria.id)
    total_setores = setores.count()

    myFilter = SectorFilter(request.GET, queryset=setores)
    setores = myFilter.qs
    
    context = {
        'diretoria': diretoria,
        'setores': setores,
        'myFilter': myFilter,
        'total_setores': total_setores,
    }
    return render(request, 'setores/diretoria_detail.html', context)

def direction_update(request, slug):
    diretoria = get_object_or_404(Direction, slug=slug)
    form = DirectionForm(instance=diretoria)
    diretorias = Direction.objects.all()

    myFilter = DirectionFilter(request.GET, queryset=diretorias)
    diretorias = myFilter.qs

    context = {
        'diretorias': diretorias,
        'form': form,
        'diretoria': diretoria,
        'myFilter': myFilter,
        'btn': 'Atualizar Diretoria'
        }

    if request.method == 'POST':
        form = DirectionForm(request.POST, instance=diretoria)
        if form.is_valid():
            return extract_update_form_direction(form, request)
        else:
            return render(request, 'setores/diretorias.html', context)
    elif request.method == 'GET':
        return render(request, 'setores/diretorias.html', context)
    
    return redirect('dashboard:diretorias')


def extract_update_form_direction(form, request):
    diretoria = form.save(commit=False)
    diretoria.name = form.cleaned_data['name']
    diretoria.accountable = form.cleaned_data['accountable']
    diretoria.kind = form.cleaned_data['kind']

    diretoria.save()

    messages.add_message(request, constants.SUCCESS, 'Atualizado com Sucesso!')
    return redirect(reverse('dashboard:diretorias'))


def direction_delete(request, id, slug):
    diretoria = get_object_or_404(Direction, id=id, slug=slug)
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
        'btn': 'Adicionar novo Setor'
        }
    return render(request, 'setores/setores.html', context)


def sector_detail(request, slug):
    setor = get_object_or_404(Sector, slug=slug)
    context = {
            'setor': setor,
        }
    return render(request, 'setores/setor_detail.html', context)


def sector_update(request, slug):
    setor = get_object_or_404(Sector, slug=slug)
    form = SectorForm(instance=setor)
    setores = Sector.objects.all()

    myFilter = SectorFilter(request.GET, queryset=setores)
    setores = myFilter.qs

    context = {
        'setores': setores,
        'form': form,
        'setor': setor,
        'myFilter': myFilter,
        'btn': 'Atualizar Setor'
        }

    if request.method == 'POST':
        form = SectorForm(request.POST, instance=setor)
        if form.is_valid():
            return extract_update_form_sector(form, request)
        else:
            return render(request, 'setores/setores.html', context)
    elif request.method == 'GET':
        return render(request, 'setores/setores.html', context)
    
    return redirect('dashboard:setores')


def extract_update_form_sector(form, request):
    setor = form.save(commit=False)
    setor.name = form.cleaned_data['name']
    setor.accountable = form.cleaned_data['accountable']
    setor.direction = form.cleaned_data['direction']
    setor.phone = form.cleaned_data['phone']
    setor.email = form.cleaned_data['email']
    setor.address = form.cleaned_data['address']

    setor.save()

    messages.add_message(request, constants.SUCCESS, 'Atualizado com Sucesso!')
    return redirect(reverse('dashboard:setores'))


def sector_delete(request, id, slug):
    setor = get_object_or_404(Sector, id=id, slug=slug)
    setor.delete()
    messages.add_message(request, constants.ERROR, f'O Setor {setor.name} foi excluido com sucesso!')
    return redirect(reverse('dashboard:setores'))