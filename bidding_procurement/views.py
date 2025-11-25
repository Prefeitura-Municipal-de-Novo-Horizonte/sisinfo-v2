from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

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
    MaterialBidding,
)
from reports.models import MaterialReport


@login_required
def biddings(request):
    licitacoes = Bidding.objects.all()
    if request.method == "POST":
        form = BiddingForm(request.POST)
        if form.is_valid():
            form.save()
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
    licitacao = get_object_or_404(Bidding, slug=slug)
    # Materiais agora vêm de MaterialBidding (tabela intermediária)
    material_associations = licitacao.material_associations.all().select_related('material', 'supplier')
    total_materiais = material_associations.count()
    if request.method == "POST":
        form_material = MaterialBiddingForm(request.POST)
        if form_material.is_valid():
            material_bidding = form_material.save(commit=False)
            material_bidding.bidding = licitacao
            try:
                material_bidding.save()
                messages.add_message(request, constants.SUCCESS,
                                     "Material vinculado com sucesso!")
            except IntegrityError:
                messages.add_message(request, constants.ERROR, "Este material já está vinculado a esta licitação!")
        else:
            messages.add_message(request, constants.ERROR, "Erro ao vincular material. Verifique os dados.")
        return redirect("bidding_procurement:licitacao", slug=slug)

    form_material = MaterialBiddingForm()
    myFilter = MaterialFilter(request.GET, queryset=Material.objects.all())
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
    licitacao = get_object_or_404(Bidding, slug=slug)
    form = BiddingForm(instance=licitacao)
    licitacoes = Bidding.objects.all()
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
        if form.is_valid():
            form.save()
            messages.add_message(request, constants.SUCCESS, "Atualizado com Sucesso!")
            return redirect("bidding_procurement:licitacoes")
        else:
            return render(request, "bidding_procurement/biddings.html", context)
    elif request.method == "GET":
        return render(request, "bidding_procurement/biddings.html", context)

    return redirect("bidding_procurement:licitacao")





@login_required
@login_required
def bidding_delete(request, slug):
    licitacao = get_object_or_404(Bidding, slug=slug)
    licitacao.delete()
    messages.add_message(
        request,
        constants.ERROR,
        f"A licitação {licitacao.name} foi excluido com sucesso!",
    )
    return redirect("bidding_procurement:licitacoes")


@login_required
def toggle_bidding_status(request, slug):
    licitacao = get_object_or_404(Bidding, slug=slug)
    
    # Toggle status: '1' (Ativo) <-> '2' (Inativo)
    if licitacao.status == '1':
        licitacao.status = '2'
        msg = f"A licitação {licitacao.name} foi desativada com sucesso!"
    else:
        licitacao.status = '1'
        msg = f"A licitação {licitacao.name} foi ativada com sucesso!"
    
    licitacao.save()  # O método save() já propaga para os materiais
    
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect("bidding_procurement:licitacoes")


@login_required
def toggle_material_status(request, id):
    material_bidding = get_object_or_404(MaterialBidding, id=id)
    
    # Toggle status: '1' (Ativo) <-> '2' (Inativo)
    if material_bidding.status == '1':
        material_bidding.status = '2'
        msg = f"O material {material_bidding.material.name} foi desativado nesta licitação!"
    else:
        material_bidding.status = '1'
        msg = f"O material {material_bidding.material.name} foi ativado nesta licitação!"
    
    material_bidding.save()
    
    messages.add_message(request, constants.SUCCESS, msg)
    return redirect("bidding_procurement:licitacao", slug=material_bidding.bidding.slug)


@login_required
def materials(request):
    materiais = Material.objects.all()
    total_materiais = materiais.count()
    if request.method == "POST":
        form_material = MaterialForm(request.POST)
        if form_material.is_valid():
            form_material.save()
            messages.add_message(request, constants.SUCCESS,
                                 "Inserido com sucesso!")
        else:
            messages.add_message(request, constants.ERROR, "Ocorreu um erro!")
        return redirect("bidding_procurement:materiais")
    form_material = MaterialForm()
    myFilter = MaterialFilter(request.GET, queryset=materiais)
    materiais = myFilter.qs
    context = {
        "form": form_material,
        "materiais": materiais,
        "btn": "Adicionar novo material",
        "myFilter": myFilter,
        "total_materiais": total_materiais,
    }
    return render(request, "bidding_procurement/materials.html", context)


@login_required
def material_detail(request, slug):
    material = get_object_or_404(Material, slug=slug)
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
    material = get_object_or_404(Material, slug=slug)
    form_material = MaterialForm(instance=material)
    materiais = Material.objects.all()
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
        if form_material.is_valid():
            form_material.save()
            messages.add_message(request, constants.SUCCESS, "Atualizado com Sucesso!")
            return redirect("bidding_procurement:materiais")
        else:
            return render(request, "bidding_procurement/materials.html", context)
    elif request.method == "GET":
        return render(request, "bidding_procurement/materials.html", context)

    return redirect("bidding_procurement:licitacao")





@login_required
@login_required
def material_delete(request, slug):
    material = get_object_or_404(Material, slug=slug)
    material.delete()
    messages.add_message(
        request,
        constants.ERROR,
        f"O suprimento {material.name} foi excluido com sucesso!",
    )
    return redirect("bidding_procurement:materiais")
