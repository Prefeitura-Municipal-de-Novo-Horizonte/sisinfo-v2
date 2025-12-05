from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from authenticate.decorators import tech_only
from bidding_supplier.forms import ContactForm, ContactInlineForm, SupplierForm
from bidding_supplier.models import Contact, Supplier
from bidding_supplier.services import SupplierService


# Create your views here.
@login_required(login_url='login')
def suppliers(request):
    """
    View para listar e criar fornecedores.
    
    GET: Lista todos os fornecedores.
    POST: Cria um novo fornecedor com contatos.
    """
    suppliers_list = SupplierService.get_all_suppliers()
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        form_contact_factory = inlineformset_factory(
            Supplier, Contact, form=ContactForm)
        form_contact = form_contact_factory(request.POST)
        
        if SupplierService.create_supplier(form, form_contact):
            messages.add_message(
                request, constants.SUCCESS, "Um novo fornecedor inserido com sucesso")
        else:
            messages.add_message(request, constants.ERROR, "Ocorreu um erro!")
        return redirect(reverse("suppliers:fornecedores"))
        
    form = SupplierForm()
    form_contact = inlineformset_factory(
        Supplier, Contact, form=ContactForm, extra=2)
    context = {
        'suppliers': suppliers_list,
        'form': form,
        'form_contact': form_contact,
        'btn': 'Adicionar novo Fornecedor',
    }
    return render(request, "suppliers.html", context)


@login_required(login_url='login')
def supplier_update(request, slug):
    """
    View para atualizar um fornecedor existente e seus contatos.
    """
    supplier = SupplierService.get_supplier_by_slug(slug)
    form = SupplierForm(request.POST or None, instance=supplier, prefix='main')
    form_contact = ContactInlineForm(
        request.POST or None, instance=supplier, prefix='suppliers')
    suppliers_list = SupplierService.get_all_suppliers()

    if request.method == 'POST':
        if SupplierService.update_supplier(form, form_contact):
            messages.add_message(
                request, constants.SUCCESS, f'O fornecedor {supplier.trade} foi atualizado com sucesso')
            return redirect(reverse('suppliers:fornecedor_update', kwargs={'slug': slug}))
        messages.add_message(request, constants.WARNING,
                             f'Não foi possível atualizar o fornecedor {supplier.trade}')
        return redirect(reverse('suppliers:fornecedor_update', kwargs={'slug': slug}))
    context = {
        'form': form,
        'supplier': supplier,
        'form_contact': form_contact,
        'suppliers': suppliers_list,
        'btn': 'Atualizar Fornecedor'
    }
    return render(request, 'supplier_update.html', context)


@login_required(login_url='login')
def supplier_detail(request, slug):
    """
    View para exibir detalhes de um fornecedor, incluindo contatos, materiais e licitações.
    """
    context = SupplierService.get_supplier_details(slug)
    return render(request, 'supplier_detail.html', context)


@login_required(login_url='login')
@tech_only
def supplier_delete(request, slug):
    """
    View para excluir um fornecedor (apenas técnicos).
    """
    supplier = get_object_or_404(Supplier, slug=slug)
    trade = supplier.trade
    if SupplierService.delete_supplier(supplier):
        messages.add_message(request, constants.ERROR,
                             f'O Fornecedor {trade} foi excluido com sucesso!')
        return redirect(reverse('suppliers:fornecedores'))
    messages.add_message(request, constants.WARNING,
                         f'Não foi possivel excluir o fornecedor {trade}')
    return redirect(reverse('suppliers:fornecedores'))


@login_required(login_url='login')
def contact_supplier_delete(request, id):
    """
    View para excluir um contato de fornecedor.
    """
    supplier, msg = SupplierService.delete_contact(id)
    messages.add_message(request, constants.ERROR, msg)
    return redirect(reverse('suppliers:fornecedor_update', kwargs={'slug': supplier.slug}))
