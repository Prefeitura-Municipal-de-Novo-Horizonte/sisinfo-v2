from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import resolve_url as r
from django.urls import reverse

from authenticate.decorators import tech_only
from bidding_supplier.forms import ContactForm, ContactInlineForm, SupplierForm
from bidding_supplier.models import Contact, Supplier
from dashboard.models import Bidding, Material, MaterialBidding


# Create your views here.
@login_required(login_url='login')
def suppliers(request):
    suppliers = Supplier.objects.all()
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        form_contact_factory = inlineformset_factory(
            Supplier, Contact, form=ContactForm)
        form_contact = form_contact_factory(request.POST)
        if form.is_valid() and form_contact.is_valid():
            supplier = form.save()
            form_contact.instance = supplier
            form_contact.save()
            messages.add_message(
                request, constants.SUCCESS, "Um novo fornecedor inserido com sucesso")
        else:
            messages.add_message(request, constants.ERROR, "Ocorreu um erro!")
        return redirect(reverse("suppliers:fornecedores"))
    form = SupplierForm()
    form_contact = inlineformset_factory(
        Supplier, Contact, form=ContactForm, extra=2)
    context = {
        'suppliers': suppliers,
        'form': form,
        'form_contact': form_contact,
        'btn': 'Adicionar novo Fornecedor',
    }
    return render(request, "suppliers.html", context)


@login_required(login_url='login')
def supplier_update(request, slug):
    supplier = get_object_or_404(Supplier, slug=slug)
    form = SupplierForm(request.POST or None, instance=supplier, prefix='main')
    form_contact = ContactInlineForm(
        request.POST or None, instance=supplier, prefix='suppliers')
    suppliers = Supplier.objects.all()

    if request.method == 'POST':
        if (form.is_valid() and form_contact.is_valid()):
            form.save()
            form_contact.save()
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
        'suppliers': suppliers,
        'btn': 'Atualizar Fornecedor'
    }
    return render(request, 'supplier_update.html', context)


@login_required(login_url='login')
def supplier_detail(request, slug):
    supplier = get_object_or_404(Supplier, slug=slug)
    contacts = Contact.objects.filter(supplier=supplier)
    materials = MaterialBidding.objects.filter(supplier=supplier)
    biddings = Bidding.objects.filter(material_associations__supplier=supplier).distinct()
    context = {
        'supplier': supplier,
        'contacts': contacts,
        'materials': materials,
        'biddings': biddings,
    }
    return render(request, 'supllier.html', context)


@login_required(login_url='login')
@tech_only
def supplier_delete(request, slug, id):
    supplier = get_object_or_404(Supplier, id=id, slug=slug)
    if supplier.delete():
        messages.add_message(request, constants.ERROR,
                             f'O Fornecedor {supplier.trade} foi excluido com sucesso!')
        return redirect(reverse('suppliers:fornecedores'))
    messages.add_message(request, constants.WARNING,
                         f'Não foi possivel excluir o fornecedor {supplier.trade}')
    return redirect(reverse('suppliers:fornecedores'))


@login_required(login_url='login')
def contact_supplier_delete(request, id):
    contact = get_object_or_404(Contact, id=id)
    supplier = contact.supplier
    contact.delete()
    messages.add_message(request, constants.ERROR,
                         f'O contato {contact.value} do fornecedor {supplier.trade} foi excluido com sucesso!')
    return redirect(reverse('suppliers:fornecedor_update', kwargs={'slug': supplier.slug}))
