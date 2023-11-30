from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import resolve_url as r
from django.urls import reverse

from bidding_supplier.forms import ContactForm, ContactInlineForm, SupplierForm
from bidding_supplier.models import Contact, Supplier


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


def supplier_detail(request, slug):
    return HttpResponse(f'{slug}')
