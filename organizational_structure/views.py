from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from organizational_structure.filters import DirectionFilter, SectorFilter
from organizational_structure.forms import DirectionForm, SectorForm
from organizational_structure.models import Direction, Sector
from reports.models import Report


##############################################
@login_required
def directions(request):
    diretorias = Direction.objects.all()
    if request.method == "POST":
        form = DirectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, constants.SUCCESS,
                                 "Inserido com sucesso!")
        else:
            messages.add_message(request, constants.ERROR, "Ocorreu um erro!")
        return redirect("organizational_structure:diretorias")
    form = DirectionForm()

    myFilter = DirectionFilter(request.GET, queryset=diretorias)
    diretorias = myFilter.qs

    context = {
        "form": form,
        "diretorias": diretorias,
        "myFilter": myFilter,
        "btn": "Adicionar nova Diretoria",
        "submit_class": "text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
        "cancel_class": "text-blue-700 hover:text-white border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:hover:bg-blue-500 dark:focus:ring-blue-800",
    }
    return render(request, "organizational_structure/diretorias.html", context)


@login_required
def direction_detail(request, slug):
    diretoria = get_object_or_404(Direction, slug=slug)
    setores = Sector.objects.filter(direction=diretoria.id)
    total_setores = setores.count()
    myFilter = SectorFilter(request.GET, queryset=setores)
    setores = myFilter.qs
    paginator = Paginator(setores, 12)  # Show 15 reports per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "diretoria": diretoria,
        "page_obj": page_obj,
        "myFilter": myFilter,
        "total_setores": total_setores,
    }
    return render(request, "organizational_structure/diretoria_detail.html", context)


@login_required
def direction_update(request, slug):
    diretoria = get_object_or_404(Direction, slug=slug)
    form = DirectionForm(instance=diretoria)
    diretorias = Direction.objects.all()
    myFilter = DirectionFilter(request.GET, queryset=diretorias)
    diretorias = myFilter.qs
    context = {
        "diretorias": diretorias,
        "form": form,
        "diretoria": diretoria,
        "myFilter": myFilter,
        "btn": "Atualizar Diretoria",
        "submit_class": "text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
        "cancel_class": "text-blue-700 hover:text-white border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:hover:bg-blue-500 dark:focus:ring-blue-800",
    }
    if request.method == "POST":
        form = DirectionForm(request.POST, instance=diretoria)
        if form.is_valid():
            form.save()
            messages.add_message(request, constants.SUCCESS, "Atualizado com Sucesso!")
            return redirect("organizational_structure:diretorias")
        else:
            return render(request, "organizational_structure/diretorias.html", context)
    elif request.method == "GET":
        return render(request, "organizational_structure/diretorias.html", context)

    return redirect("organizational_structure:diretorias")





@login_required
@login_required
def direction_delete(request, slug):
    diretoria = get_object_or_404(Direction, slug=slug)
    diretoria.delete()
    messages.add_message(
        request,
        constants.ERROR,
        f"Diretoria {diretoria.name} foi excluida com sucesso!",
    )
    return redirect("organizational_structure:diretorias")


##############################################
@login_required
def sectors(request):
    setores = Sector.objects.all()
    if request.method == "POST":
        form = SectorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, constants.SUCCESS,
                                 "Inserido com sucesso!")
        else:
            messages.add_message(request, constants.ERROR, "Ocorreu um erro!")
        return redirect("organizational_structure:setores")
    form = SectorForm()
    myFilter = SectorFilter(request.GET, queryset=setores)
    setores = myFilter.qs
    paginator = Paginator(setores, 15)  # Show 15 reports per page.

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
    setor = get_object_or_404(Sector, slug=slug)
    reports = Report.objects.filter(sector=setor)
    context = {
        "setor": setor,
        "reports": reports,
    }
    return render(request, "organizational_structure/setor_detail.html", context)


@login_required
def sector_update(request, slug):
    setor = get_object_or_404(Sector, slug=slug)
    form = SectorForm(instance=setor)
    setores = Sector.objects.all()
    myFilter = SectorFilter(request.GET, queryset=setores)
    setores = myFilter.qs
    context = {
        "setores": setores,
        "form": form,
        "setor": setor,
        "myFilter": myFilter,
        "btn": "Atualizar Setor",
        "submit_class": "text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800",
        "cancel_class": "text-blue-700 hover:text-white border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2 dark:border-blue-500 dark:text-blue-500 dark:hover:text-white dark:hover:bg-blue-500 dark:focus:ring-blue-800",
    }
    if request.method == "POST":
        form = SectorForm(request.POST, instance=setor)
        if form.is_valid():
            form.save()
            messages.add_message(request, constants.SUCCESS, "Atualizado com Sucesso!")
            return redirect("organizational_structure:setores")
        else:
            return render(request, "organizational_structure/setores.html", context)
    elif request.method == "GET":
        return render(request, "organizational_structure/setores.html", context)

    return redirect("organizational_structure:setores")





@login_required
@login_required
def sector_delete(request, slug):
    setor = get_object_or_404(Sector, slug=slug)
    setor.delete()
    messages.add_message(
        request, constants.ERROR, f"O Setor {setor.name} foi excluido com sucesso!"
    )
    return redirect("organizational_structure:setores")
