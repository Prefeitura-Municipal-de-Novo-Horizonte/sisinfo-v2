from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from organizational_structure.filters import DirectionFilter, SectorFilter
from organizational_structure.forms import DirectionForm, SectorForm
from organizational_structure.models import Direction, Sector
from organizational_structure.services import StructureService
from reports.models import Report


##############################################
# DIRETORIAS
##############################################

@login_required
def directions(request):
    """
    View para listar diretorias com filtros.
    """
    from django.core.paginator import Paginator
    
    diretorias_list = StructureService.get_all_directions()
    myFilter = DirectionFilter(request.GET, queryset=diretorias_list)
    diretorias_list = myFilter.qs
    
    # Paginação
    paginator = Paginator(diretorias_list, 12)  # 12 itens por página (grid 3x4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "diretorias": page_obj,
        "page_obj": page_obj,
        "myFilter": myFilter,
    }
    return render(request, "organizational_structure/diretorias.html", context)


@login_required
def direction_create(request):
    """
    View para criar uma nova diretoria.
    """
    if request.method == "POST":
        form = DirectionForm(request.POST)
        if StructureService.create_direction(form):
            messages.add_message(request, constants.SUCCESS, "Diretoria criada com sucesso!")
            return redirect("organizational_structure:diretorias")
        else:
            messages.add_message(request, constants.ERROR, "Erro ao criar diretoria. Verifique os dados.")
    else:
        form = DirectionForm()

    context = {
        "form": form,
    }
    return render(request, "organizational_structure/direction_form.html", context)


@login_required
def direction_detail(request, slug):
    """
    View para visualizar detalhes de uma diretoria e seus setores.
    """
    context_data = StructureService.get_direction_details(slug)
    setores = context_data['setores']
    
    myFilter = SectorFilter(request.GET, queryset=setores)
    setores = myFilter.qs
    paginator = Paginator(setores, 12)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "diretoria": context_data['diretoria'],
        "page_obj": page_obj,
        "myFilter": myFilter,
        "total_setores": context_data['total_setores'],
    }
    return render(request, "organizational_structure/diretoria_detail.html", context)


@login_required
def direction_update(request, slug):
    """
    View para atualizar uma diretoria existente.
    """
    diretoria = StructureService.get_direction_by_slug(slug)
    
    if request.method == "POST":
        form = DirectionForm(request.POST, instance=diretoria)
        if StructureService.update_direction(form):
            messages.add_message(request, constants.SUCCESS, "Diretoria atualizada com sucesso!")
            return redirect("organizational_structure:diretorias")
        else:
            messages.add_message(request, constants.ERROR, "Erro ao atualizar diretoria.")
    else:
        form = DirectionForm(instance=diretoria)
    
    context = {
        "form": form,
        "diretoria": diretoria,
    }
    return render(request, "organizational_structure/direction_form.html", context)


@login_required
def direction_delete(request, slug):
    """
    View para excluir uma diretoria.
    """
    diretoria = get_object_or_404(Direction, slug=slug)
    name = diretoria.name
    StructureService.delete_direction(diretoria)
    messages.add_message(
        request,
        constants.ERROR,
        f"Diretoria {name} foi excluida com sucesso!",
    )
    return redirect("organizational_structure:diretorias")


##############################################
# SETORES
##############################################

@login_required
def sectors(request):
    """
    View para listar setores com filtros e paginação.
    """
    setores_list = StructureService.get_all_sectors()
    myFilter = SectorFilter(request.GET, queryset=setores_list)
    setores_list = myFilter.qs
    paginator = Paginator(setores_list, 15)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
        "myFilter": myFilter,
    }
    return render(request, "organizational_structure/setores.html", context)


@login_required
def sector_create(request):
    """
    View para criar um novo setor.
    """
    if request.method == "POST":
        form = SectorForm(request.POST)
        if StructureService.create_sector(form):
            messages.add_message(request, constants.SUCCESS, "Setor criado com sucesso!")
            return redirect("organizational_structure:setores")
        else:
            messages.add_message(request, constants.ERROR, "Erro ao criar setor. Verifique os dados.")
    else:
        form = SectorForm()

    context = {
        "form": form,
    }
    return render(request, "organizational_structure/sector_form.html", context)


@login_required
def sector_detail(request, slug):
    """
    View para visualizar detalhes de um setor e seus relatórios.
    """
    context = StructureService.get_sector_details(slug)
    return render(request, "organizational_structure/setor_detail.html", context)


@login_required
def sector_update(request, slug):
    """
    View para atualizar um setor existente.
    """
    setor = StructureService.get_sector_by_slug(slug)
    
    if request.method == "POST":
        form = SectorForm(request.POST, instance=setor)
        if StructureService.update_sector(form):
            messages.add_message(request, constants.SUCCESS, "Setor atualizado com sucesso!")
            return redirect("organizational_structure:setores")
        else:
            messages.add_message(request, constants.ERROR, "Erro ao atualizar setor.")
    else:
        form = SectorForm(instance=setor)
    
    context = {
        "form": form,
        "setor": setor,
    }
    return render(request, "organizational_structure/sector_form.html", context)


@login_required
def sector_delete(request, slug):
    """
    View para excluir um setor.
    """
    setor = get_object_or_404(Sector, slug=slug)
    name = setor.name
    StructureService.delete_sector(setor)
    messages.add_message(
        request, constants.ERROR, f"O Setor {name} foi excluido com sucesso!"
    )
    return redirect("organizational_structure:setores")
