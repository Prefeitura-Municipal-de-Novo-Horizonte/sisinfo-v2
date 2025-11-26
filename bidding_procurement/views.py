from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import redirect, render

from bidding_procurement.filters import (
    BiddingFilter,
    MaterialFilter,
)
from bidding_procurement.forms import (
    BiddingForm,
    MaterialBiddingForm,
    MaterialForm,
)
from bidding_procurement.models import (
    Bidding,
    Material,
)
from reports.models import MaterialReport
from .services import BiddingService, MaterialService


@login_required
def biddings(request):
    """
    View para listar e criar licitações.
    
    GET: Lista todas as licitações com paginação e filtro.
    POST: Cria uma nova licitação.
    """
    licitacoes = BiddingService.get_all_biddings()
    if request.method == "POST":
        form = BiddingForm(request.POST)
        if BiddingService.create_bidding(form):
            messages.add_message(request, constants.SUCCESS,
                                 "Inserido com sucesso!")
        else:
            messages.add_message(request, constants.ERROR, "Ocorreu um erro!")
        return redirect("bidding_procurement:licitacoes")
    total_licitacoes = licitacoes.count()
    form = BiddingForm()
    myFilter = BiddingFilter(request.GET, queryset=licitacoes)
    licitacoes = myFilter.qs
    
    paginator = Paginator(licitacoes, 15)  # Show 15 biddings per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "form": form,
        "page_obj": page_obj,
        "myFilter": myFilter,
        "btn": "Adicionar nova Licitação",
        "total_licitacoes": total_licitacoes,
    }
    return render(request, "bidding_procurement/biddings.html", context)


@login_required
def bidding_detail(request, slug):
    """
    View para exibir detalhes de uma licitação e vincular materiais.
    
    GET: Exibe detalhes da licitação e lista de materiais vinculados.
    POST: Vincula um novo material à licitação.
    """
    licitacao = BiddingService.get_bidding_by_slug(slug)
    # Materiais agora vêm de MaterialBidding (tabela intermediária)
    material_associations = licitacao.material_associations.all().select_related('material', 'supplier')
    total_materiais = material_associations.count()
    if request.method == "POST":
        form_material = MaterialBiddingForm(request.POST)
        success, msg = BiddingService.add_material_to_bidding(licitacao, form_material)
        if success:
            messages.add_message(request, constants.SUCCESS, msg)
        else:
            messages.add_message(request, constants.ERROR, msg)
        return redirect("bidding_procurement:licitacao", slug=slug)

    form_material = MaterialBiddingForm()
    myFilter = MaterialFilter(request.GET, queryset=MaterialService.get_all_materials())
    context = {
        "licitacao": licitacao,
        "form": form_material,
        "material_associations": material_associations,
        "myFilter": myFilter,
        "total_materiais": total_materiais,
        "btn": "Vincular Material",
    }
    return render(request, "bidding_procurement/bidding_detail.html", context)


@login_required
def bidding_update(request, slug):
    """
    View para atualizar uma licitação existente.
    """
    licitacao = BiddingService.get_bidding_by_slug(slug)
    form = BiddingForm(instance=licitacao)
    licitacoes = BiddingService.get_all_biddings()
    myFilter = BiddingFilter(request.GET, queryset=licitacoes)
    licitacoes = myFilter.qs
    context = {
        "licitacao": licitacao,
        "licitacoes": licitacoes,
        "form": form,
        "myFilter": myFilter,
        "btn": "Atualizar Licitação",
    }

    if request.method == "POST":
        form = BiddingForm(request.POST, instance=licitacao)
        if BiddingService.update_bidding(licitacao, form):
            messages.add_message(request, constants.SUCCESS, "Atualizado com Sucesso!")
            return redirect("bidding_procurement:licitacoes")
        else:
            return render(request, "bidding_procurement/biddings.html", context)
    elif request.method == "GET":
        return render(request, "bidding_procurement/biddings.html", context)

    return redirect("bidding_procurement:licitacao")


@login_required
def bidding_delete(request, slug):
    """
    View para excluir uma licitação.
    """
    licitacao = BiddingService.get_bidding_by_slug(slug)
    name = licitacao.name
    BiddingService.delete_bidding(licitacao)
    messages.add_message(
        request,
        constants.ERROR,
        f"A licitação {name} foi excluido com sucesso!",
    )
    return redirect("bidding_procurement:licitacoes")


@login_required
def toggle_bidding_status(request, slug):
    """
    View para alternar o status de uma licitação (Ativo/Inativo).
    """
    licitacao = BiddingService.get_bidding_by_slug(slug)
    msg = BiddingService.toggle_status(licitacao)
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect("bidding_procurement:licitacoes")


@login_required
def toggle_material_status(request, id):
    """
    View para alternar o status de um material em uma licitação específica.
    """
    material_bidding, msg = BiddingService.toggle_material_status(id)
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect("bidding_procurement:licitacao", slug=material_bidding.bidding.slug)


@login_required
def materials(request):
    """
    View para listar e criar materiais.
    
    GET: Lista todos os materiais com paginação e filtro.
    POST: Cria um novo material.
    """
    materiais = MaterialService.get_all_materials()
    total_materiais = materiais.count()
    if request.method == "POST":
        form_material = MaterialForm(request.POST)
        if MaterialService.create_material(form_material):
            messages.add_message(request, constants.SUCCESS,
                                 "Inserido com sucesso!")
        else:
            messages.add_message(request, constants.ERROR, "Ocorreu um erro!")
        return redirect("bidding_procurement:materiais")
    form_material = MaterialForm()
    myFilter = MaterialFilter(request.GET, queryset=materiais)
    materiais = myFilter.qs
    
    paginator = Paginator(materiais, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "form": form_material,
        "page_obj": page_obj,
        "btn": "Adicionar novo material",
        "myFilter": myFilter,
        "total_materiais": total_materiais,
    }
    return render(request, "bidding_procurement/materials.html", context)


@login_required
def material_detail(request, slug):
    """
    View para exibir detalhes de um material e seu histórico de uso.
    """
    material = MaterialService.get_material_by_slug(slug)
    reports = MaterialReport.objects.filter(material=material.id)
    total_quantity = reports.aggregate(total_value=Sum("quantity"))
    total_quantity = total_quantity.get("total_value")
    context = {
        "material": material,
        "reports": reports,
        "total_quantity": total_quantity,
    }
    return render(request, "bidding_procurement/material_detail.html", context)


@login_required
def material_update(request, slug):
    """
    View para atualizar um material existente.
    """
    material = MaterialService.get_material_by_slug(slug)
    form_material = MaterialForm(instance=material)
    materiais = MaterialService.get_all_materials()
    myFilter = MaterialFilter(request.GET, queryset=materiais)
    materiais = myFilter.qs
    context = {
        "material": material,
        "materiais": materiais,
        "form": form_material,
        "myFilter": myFilter,
        "btn": "Atualizar Material",
    }

    if request.method == "POST":
        form_material = MaterialForm(request.POST, instance=material)
        if MaterialService.update_material(material, form_material):
            messages.add_message(request, constants.SUCCESS, "Atualizado com Sucesso!")
            return redirect("bidding_procurement:materiais")
        else:
            return render(request, "bidding_procurement/materials.html", context)
    elif request.method == "GET":
        return render(request, "bidding_procurement/materials.html", context)

    return redirect("bidding_procurement:licitacao")


@login_required
def material_delete(request, slug):
    """
    View para excluir um material.
    """
    material = MaterialService.get_material_by_slug(slug)
    name = material.name
    MaterialService.delete_material(material)
    messages.add_message(
        request,
        constants.ERROR,
        f"O suprimento {name} foi excluido com sucesso!",
    )
    return redirect("bidding_procurement:materiais")
