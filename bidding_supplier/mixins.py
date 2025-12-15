"""
Mixins reutilizáveis para views do bidding_supplier.
"""
from django.contrib import messages
from django.contrib.messages import constants


class MessageMixin:
    """
    Mixin para adicionar mensagens de feedback automáticas.
    """
    success_message = ""
    error_message = ""
    
    def form_valid(self, form):
        """Adiciona mensagem de sucesso se definida."""
        if self.success_message:
            messages.add_message(
                self.request,
                constants.SUCCESS,
                self.success_message
            )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Adiciona mensagem de erro se definida."""
        if self.error_message:
            messages.add_message(
                self.request,
                constants.ERROR,
                self.error_message
            )
        return super().form_invalid(form)


class FormsetMixin:
    """
    Mixin para views que utilizam formsets (ex: Supplier + Contacts).
    """
    formset_class = None
    
    def get_context_data(self, **kwargs):
        """Adiciona formset ao contexto."""
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['formset'] = self.formset_class(
                self.request.POST, 
                instance=self.object if hasattr(self, 'object') else None
            )
        else:
            context['formset'] = self.formset_class(
                instance=self.object if hasattr(self, 'object') else None
            )
        
        return context
    
    def form_valid(self, form):
        """Valida e salva o formset junto com o form principal."""
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
