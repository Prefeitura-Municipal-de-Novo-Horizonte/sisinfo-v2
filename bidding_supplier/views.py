from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages import constants
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    View,
)

from core.mixins import TechOnlyMixin, MessageMixin, FormsetMixin
from bidding_supplier.filters import SupplierFilter
from bidding_supplier.forms import ContactForm, ContactInlineForm, SupplierForm
from bidding_supplier.models import Contact, Supplier
from bidding_supplier.services import SupplierService


# ==================== SUPPLIER VIEWS ====================

class SupplierListView(LoginRequiredMixin, ListView):
    """
    View para listar fornecedores com filtros e paginação.
    """
    model = Supplier
    template_name = "suppliers.html"
    context_object_name = "suppliers"
    filterset_class = SupplierFilter
    paginate_by = 15
    
    def get_queryset(self):
        """Aplica filtros ao queryset."""
        queryset = SupplierService.get_all_suppliers()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        """Adiciona form e filtros ao contexto."""
        context = super().get_context_data(**kwargs)
        context['form'] = SupplierForm()
        context['form_contact'] = ContactInlineForm()
        context['myFilter'] = self.filterset
        context['btn'] = 'Adicionar novo Fornecedor'
        return context


class SupplierCreateView(LoginRequiredMixin, MessageMixin, FormsetMixin, CreateView):
    """
    View para criar um novo fornecedor com contatos.
    """
    model = Supplier
    form_class = SupplierForm
    formset_class = ContactInlineForm
    template_name = "suppliers.html"
    success_url = reverse_lazy("suppliers:fornecedores")
    success_message = "Um novo fornecedor inserido com sucesso"
    error_message = "Ocorreu um erro!"
    
    def get_context_data(self, **kwargs):
        """Adiciona lista de fornecedores ao contexto."""
        context = super().get_context_data(**kwargs)
        context['suppliers'] = SupplierService.get_all_suppliers()
        context['btn'] = 'Adicionar novo Fornecedor'
        return context


class SupplierDetailView(LoginRequiredMixin, DetailView):
    """
    View para exibir detalhes de um fornecedor.
    """
    model = Supplier
    template_name = "supplier_detail.html"
    context_object_name = "supplier"
    
    def get_context_data(self, **kwargs):
        """Adiciona contatos, materiais e licitações ao contexto."""
        context = super().get_context_data(**kwargs)
        details = SupplierService.get_supplier_details(self.object.slug)
        context.update(details)
        return context


class SupplierUpdateView(LoginRequiredMixin, MessageMixin, FormsetMixin, UpdateView):
    """
    View para atualizar um fornecedor e seus contatos.
    """
    model = Supplier
    form_class = SupplierForm
    formset_class = ContactInlineForm
    template_name = "supplier_update.html"
    context_object_name = "supplier"
    
    def get_success_url(self):
        """Retorna para a própria página de edição."""
        return reverse_lazy('suppliers:fornecedor_update', kwargs={'slug': self.object.slug})
    
    def get_success_message(self):
        """Mensagem dinâmica com nome do fornecedor."""
        return f'O fornecedor {self.object.trade} foi atualizado com sucesso'
    
    def get_form(self, form_class=None):
        """Adiciona prefix ao form principal."""
        form = super().get_form(form_class)
        form.prefix = 'main'
        return form
    
    def get_context_data(self, **kwargs):
        """Adiciona lista de fornecedores e formset ao contexto."""
        context = super().get_context_data(**kwargs)
        
        # Formset com prefix
        if self.request.POST:
            context['formset'] = self.formset_class(
                self.request.POST, 
                instance=self.object,
                prefix='suppliers'
            )
        else:
            context['formset'] = self.formset_class(
                instance=self.object,
                prefix='suppliers'
            )
        
        context['form_contact'] = context['formset']  # Alias para compatibilidade
        context['suppliers'] = SupplierService.get_all_suppliers()
        context['btn'] = 'Atualizar Fornecedor'
        return context
    
    def form_valid(self, form):
        """Valida e salva form + formset."""
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            
            messages.add_message(
                self.request,
                constants.SUCCESS,
                self.get_success_message()
            )
            return redirect(self.get_success_url())
        else:
            messages.add_message(
                self.request,
                constants.WARNING,
                f'Não foi possível atualizar o fornecedor {self.object.trade}'
            )
            return self.form_invalid(form)


class SupplierDeleteView(LoginRequiredMixin, TechOnlyMixin, View):
    """
    View para excluir um fornecedor (apenas técnicos).
    """
    def get(self, request, slug):
        """Exclui o fornecedor e redireciona."""
        supplier = get_object_or_404(Supplier, slug=slug)
        trade = supplier.trade
        
        if SupplierService.delete_supplier(supplier):
            messages.add_message(
                request,
                constants.ERROR,
                f'O Fornecedor {trade} foi excluído com sucesso!'
            )
        else:
            messages.add_message(
                request,
                constants.WARNING,
                f'Não foi possível excluir o fornecedor {trade}'
            )
        
        return redirect(reverse_lazy('suppliers:fornecedores'))


class ContactDeleteView(LoginRequiredMixin, View):
    """
    View para excluir um contato de fornecedor.
    """
    def get(self, request, id):
        """Exclui o contato e redireciona."""
        supplier, msg = SupplierService.delete_contact(id)
        messages.add_message(request, constants.ERROR, msg)
        return redirect(reverse_lazy('suppliers:fornecedor_update', kwargs={'slug': supplier.slug}))
