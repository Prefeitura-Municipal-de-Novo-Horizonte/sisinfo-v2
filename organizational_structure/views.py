from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
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
@login_required
def directions(request):
    """
    View para listar e criar diretorias.
    
    GET: Lista todas as diretorias com filtro.
    POST: Cria uma nova diretoria.
    """
    diretorias_list = StructureService.get_all_directions()
    if request.method == "POST":
        form = DirectionForm(request.POST)
        if StructureService.create_direction(form):
            messages.add_message(request, constants.SUCCESS,
                                 "Inserido com sucesso!")
        else:
            messages.add_message(request, constants.ERROR, "Ocorreu um erro!")
        return redirect("organizational_structure:diretorias")
    form = DirectionForm()

    myFilter = DirectionFilter(request.GET, queryset=diretorias_list)
    diretorias_list = myFilter.qs

    context = {
        "form": form,
        "diretorias": diretorias_list,
        "myFilter": myFilter,
        "btn": "Adicionar nova Diretoria",
        "submit_class": "text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
        "cancel_class": "text-blue-700 hover:text-white border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:hover:bg-blue-500 dark:focus:ring-blue-800",
    }
    return render(request, "organizational_structure/diretorias.html", context)


@login_required
def direction_detail(request, slug):
    """
    View para visualizar detalhes de uma diretoria e seus setores.
    """
    context_data = StructureService.get_direction_details(slug)
    setores = context_data['setores']
    
    myFilter = SectorFilter(request.GET, queryset=setores)
    setores = myFilter.qs
    paginator = Paginator(setores, 12)  # Show 15 reports per page.

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
    form = DirectionForm(instance=diretoria)
    diretorias_list = StructureService.get_all_directions()
    myFilter = DirectionFilter(request.GET, queryset=diretorias_list)
    diretorias_list = myFilter.qs
    
    context = {
        "diretorias": diretorias_list,
        "form": form,
        "diretoria": diretoria,
        "myFilter": myFilter,
        "btn": "Atualizar Diretoria",
        "submit_class": "text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
        "cancel_class": "text-blue-700 hover:text-white border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:hover:bg-blue-500 dark:focus:ring-blue-800",
    }
    if request.method == "POST":
        form = DirectionForm(request.POST, instance=diretoria)
        if StructureService.update_direction(form):
            messages.add_message(request, constants.SUCCESS, "Atualizado com Sucesso!")
            return redirect("organizational_structure:diretorias")
        else:
            return render(request, "organizational_structure/diretorias.html", context)
    elif request.method == "GET":
        return render(request, "organizational_structure/diretorias.html", context)

    return redirect("organizational_structure:diretorias")


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
@login_required
def sectors(request):
    """
    View para listar e criar setores.
    
    GET: Lista todos os setores com paginação e filtro.
    POST: Cria um novo setor.
    """
    setores_list = StructureService.get_all_sectors()
    if request.method == "POST":
        form = SectorForm(request.POST)
        if StructureService.create_sector(form):
            messages.add_message(request, constants.SUCCESS,
                                 "Inserido com sucesso!")
        else:
            messages.add_message(request, constants.ERROR, "Ocorreu um erro!")
        return redirect("organizational_structure:setores")
        
    form = SectorForm()
    myFilter = SectorFilter(request.GET, queryset=setores_list)
    setores_list = myFilter.qs
    paginator = Paginator(setores_list, 15)  # Show 15 reports per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "form": form,
        "page_obj": page_obj,
        "myFilter": myFilter,
        "btn": "Adicionar novo Setor",
        "submit_class": "text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
        "cancel_class": "text-blue-700 hover:text-white border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:hover:bg-blue-500 dark:focus:ring-blue-800",
    }
    return render(request, "organizational_structure/setores.html", context)


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
    form = SectorForm(instance=setor)
    setores_list = StructureService.get_all_sectors()
    myFilter = SectorFilter(request.GET, queryset=setores_list)
    setores_list = myFilter.qs
    
    context = {
        "setores": setores_list,
        "form": form,
        "setor": setor,
        "myFilter": myFilter,
        "btn": "Atualizar Setor",
        "submit_class": "text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
        "cancel_class": "text-blue-700 hover:text-white border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:hover:bg-blue-500 dark:focus:ring-blue-800",
    }
    if request.method == "POST":
        form = SectorForm(request.POST, instance=setor)
        if StructureService.update_sector(form):
            messages.add_message(request, constants.SUCCESS, "Atualizado com Sucesso!")
            return redirect("organizational_structure:setores")
        else:
            return render(request, "organizational_structure/setores.html", context)
    elif request.method == "GET":
        return render(request, "organizational_structure/setores.html", context)

    return redirect("organizational_structure:setores")


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
