from django.contrib import messages
from django.contrib.messages import constants
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import resolve_url as r
from django.urls import reverse

from dashboard.filters import (
    BiddingFilter,
    DirectionFilter,
    MaterialFilter,
    SectorFilter,
)
from dashboard.forms import BiddingForm, DirectionForm, MaterialForm, SectorForm
from dashboard.models import Bidding, Direction, Material, Sector


# Create your views here.
def index(request):
    context = {}
    return render(request, 'index.html', context)


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
    messages.add_message(request, constants.ERROR, f'Diretoria {
                         diretoria.name} foi excluida com sucesso!')
    return redirect(reverse('dashboard:diretorias'))


##############################################
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
    messages.add_message(request, constants.ERROR, f'O Setor {
                         setor.name} foi excluido com sucesso!')
    return redirect(reverse('dashboard:setores'))


##############################################
def biddings(request):
    licitacoes = Bidding.objects.all()
    if request.method == 'POST':
        form = BiddingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, constants.SUCCESS,
                                 'Inserido com sucesso!')
        else:
            messages.add_message(request, constants.ERROR, 'Ocorreu um erro!')
        return redirect(reverse('dashboard:licitacoes'))
    total_licitacoes = licitacoes.count()
    form = BiddingForm()
    myFilter = BiddingFilter(request.GET, queryset=licitacoes)
    licitacoes = myFilter.qs

    context = {
        'form': form,
        'licitacoes': licitacoes,
        'myFilter': myFilter,
        'btn': 'Adicionar nova Licitação',
        'total_licitacoes': total_licitacoes,
    }
    return render(request, 'licitacao/biddings.html', context)


def bidding_detail(request, slug):
    licitacao = get_object_or_404(Bidding, slug=slug)
    materiais = Material.objects.filter(bidding=licitacao.id)
    total_materiais = materiais.count()
    if request.method == 'POST':
        form_material = MaterialForm(request.POST)
        if form_material.is_valid():
            form_material.save()
            messages.add_message(request, constants.SUCCESS,
                                 'Inserido com sucesso!')
        else:
            messages.add_message(request, constants.ERROR, 'Ocorreu um erro!')
        return redirect(reverse('dashboard:licitacao', kwargs={'slug': slug}))

    form_material = MaterialForm()
    myFilter = MaterialFilter(request.GET, queryset=materiais)
    materiais = myFilter.qs
    context = {
        'licitacao': licitacao,
        'form': form_material,
        'materiais': materiais,
        'myFilter': myFilter,
        'total_materiais': total_materiais,
        'btn': 'Adicionar Material'
    }
    return render(request, 'licitacao/bidding_detail.html', context)


def bidding_update(request, slug):
    licitacao = get_object_or_404(Bidding, slug=slug)
    form = BiddingForm(instance=licitacao)
    licitacoes = Bidding.objects.all()
    myFilter = BiddingFilter(request.GET, queryset=licitacoes)
    licitacoes = myFilter.qs
    context = {
        'licitacao': licitacao,
        'licitacoes': licitacoes,
        'form': form,
        'myFilter': myFilter,
        'btn': 'Atualizar Licitação'
    }

    if request.method == 'POST':
        form = BiddingForm(request.POST, instance=licitacao)
        if form.is_valid():
            return extract_update_form_bidding(form, request)
        else:
            return render(request, 'licitacao/biddings.html', context)
    elif request.method == 'GET':
        return render(request, 'licitacao/biddings.html', context)

    return redirect('dashboard:licitacao')


def extract_update_form_bidding(form, request):
    licitacao = form.save(commit=False)
    licitacao.name = form.cleaned_data['name']
    licitacao.status = form.cleaned_data['status']
    licitacao.date = form.cleaned_data['date']
    licitacao.save()
    messages.add_message(request, constants.SUCCESS, 'Atualizado com Sucesso!')
    return redirect(reverse('dashboard:licitacoes'))


def bidding_delete(request, slug, id):
    licitacao = get_object_or_404(Bidding, id=id, slug=slug)
    licitacao.delete()
    messages.add_message(request, constants.ERROR, f'O Setor {
                         licitacao.name} foi excluido com sucesso!')
    return redirect(reverse('dashboard:licitacoes'))


def materials(request):
    materiais = Material.objects.all()
    total_materiais = materiais.count()
    if request.method == 'POST':
        form_material = MaterialForm(request.POST)
        if form_material.is_valid():
            form_material.save()
            messages.add_message(request, constants.SUCCESS,
                                 'Inserido com sucesso!')
        else:
            messages.add_message(request, constants.ERROR, 'Ocorreu um erro!')
        return redirect(reverse('dashboard:materiais'))
    form_material = MaterialForm()
    myFilter = MaterialFilter(request.GET, queryset=materiais)
    materiais = myFilter.qs
    context = {
        'form_material': form_material,
        'materiais': materiais,
        'btn': 'Adicionar novo material',
        'myFilter': myFilter,
        'total_materiais': total_materiais,
    }
    return render(request, 'licitacao/materials.html', context)


def material_detail(request, slug):
    material = get_object_or_404(Material, slug=slug)
    context = {
        'material': material,
    }
    return render(request, 'licitacao/material_detail.html', context)


def material_update(request, slug):
    material = get_object_or_404(Material, slug=slug)
    form_material = MaterialForm(instance=material)
    materiais = Material.objects.all()
    myFilter = MaterialFilter(request.GET, queryset=materiais)
    materiais = myFilter.qs
    context = {
        'material': material,
        'materiais': materiais,
        'form_material': form_material,
        'myFilter': myFilter,
        'btn': 'Atualizar Licitação'
    }

    if request.method == 'POST':
        form_material = MaterialForm(request.POST, instance=material)
        if form_material.is_valid():
            return extract_update_form_material(form_material, request)
        else:
            return render(request, 'licitacao/materials.html', context)
    elif request.method == 'GET':
        return render(request, 'licitacao/materials.html', context)

    return redirect('dashboard:licitacao')


def extract_update_form_material(form, request):
    material = form.save(commit=False)
    material.name = form.cleaned_data['name']
    material.status = form.cleaned_data['status']
    material.bidding = form.cleaned_data['bidding']
    material.price = form.cleaned_data['price']
    material.readjustment = form.cleaned_data['readjustment']
    material.save()
    messages.add_message(request, constants.SUCCESS, 'Atualizado com Sucesso!')
    return redirect(reverse('dashboard:materiais'))


def material_delete(request, slug, id):
    material = get_object_or_404(Material, slug=slug, id=id)
    material.delete()
    messages.add_message(request, constants.ERROR, f'O suprimento {
                         material.name} foi excluido com sucesso!')
    return redirect(reverse('dashboard:materiais'))
