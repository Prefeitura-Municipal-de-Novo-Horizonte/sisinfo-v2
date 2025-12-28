"""
Mixins compartilhados para formulários, views e outras utilidades.

Este módulo centraliza todos os mixins reutilizáveis do projeto.
"""
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


# =============================================================================
# FORM MIXINS
# =============================================================================

class CapitalizeFieldMixin:
    """
    Mixin para formulários que precisam capitalizar campos de texto.
    
    Fornece o método `extract_from_clean` que capitaliza cada palavra
    de um campo de texto.
    
    Exemplo:
        class MyForm(CapitalizeFieldMixin, forms.ModelForm):
            def clean_name(self):
                return self.extract_from_clean("name")
    """
    
    def extract_from_clean(self, field_name):
        """
        Capitaliza cada palavra de um campo de texto.
        
        Args:
            field_name (str): Nome do campo a ser capitalizado
            
        Returns:
            str: Texto com cada palavra capitalizada
        """
        name = self.cleaned_data.get(field_name)
        if name:
            words = [w.capitalize() for w in name.split()]
            return " ".join(words)
        return name


class TailwindFormMixin:
    """
    Mixin para aplicar estilos Tailwind CSS aos campos do formulário.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = "block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-brand-500 focus:outline-none focus:ring-0 focus:border-brand-600 peer"
            field.widget.attrs['placeholder'] = " "


# =============================================================================
# FILTER MIXINS
# =============================================================================

class TailwindFilterMixin:
    """
    Mixin para aplicar estilos Tailwind CSS aos campos de filtro (FilterSet).
    Estilo tipo 'Search Box' (arredondado, com fundo).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.form.fields.values():
            field.widget.attrs['class'] = "block p-2.5 pl-10 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-brand-500 dark:focus:border-brand-500"


class FilteredListMixin:
    """
    Mixin para adicionar funcionalidade de filtro django-filter às views.
    
    Attributes:
        filterset_class: Classe do filtro a ser aplicado
    """
    filterset_class = None
    
    def get_filterset(self, queryset):
        """
        Retorna o filterset configurado com o queryset.
        
        Args:
            queryset: QuerySet a ser filtrado
            
        Returns:
            Instância do filterset configurado
        """
        if self.filterset_class is None:
            raise ValueError("filterset_class deve ser definido")
        return self.filterset_class(self.request.GET, queryset=queryset)
    
    def get_queryset(self):
        """Sobrescreve get_queryset para aplicar filtros."""
        queryset = super().get_queryset()
        self.filterset = self.get_filterset(queryset)
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        """Adiciona o filterset ao contexto."""
        context = super().get_context_data(**kwargs)
        context['myFilter'] = self.filterset
        return context


# =============================================================================
# VIEW MIXINS
# =============================================================================

class MessageMixin:
    """
    Mixin para adicionar mensagens de sucesso/erro padronizadas.
    
    Attributes:
        success_message: Mensagem de sucesso (pode usar format com object)
        error_message: Mensagem de erro
    """
    success_message = None
    error_message = None
    
    def get_success_message(self):
        """Retorna a mensagem de sucesso formatada."""
        if self.success_message:
            return self.success_message.format(object=self.object)
        return "Operação realizada com sucesso!"
    
    def get_error_message(self):
        """Retorna a mensagem de erro formatada."""
        if self.error_message:
            return self.error_message
        return "Ocorreu um erro ao processar a solicitação."
    
    def form_valid(self, form):
        """Adiciona mensagem de sucesso quando o formulário é válido."""
        response = super().form_valid(form)
        messages.add_message(
            self.request,
            constants.SUCCESS,
            self.get_success_message()
        )
        return response
    
    def form_invalid(self, form):
        """Adiciona mensagem de erro quando o formulário é inválido."""
        messages.add_message(
            self.request,
            constants.ERROR,
            self.get_error_message()
        )
        return super().form_invalid(form)
    
    def delete(self, request, *args, **kwargs):
        """Adiciona mensagem ao excluir objeto."""
        self.object = self.get_object()
        success_message = self.get_success_message()
        response = super().delete(request, *args, **kwargs)
        messages.add_message(
            request,
            constants.ERROR,  # Usa ERROR para exclusões (padrão do sistema)
            success_message
        )
        return response


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


class PaginatedListMixin:
    """
    Mixin para adicionar paginação às views de listagem.
    
    Attributes:
        paginate_by: Número de itens por página (padrão: 15)
    """
    paginate_by = 15
    
    def get_context_data(self, **kwargs):
        """Adiciona informações de paginação ao contexto."""
        context = super().get_context_data(**kwargs)
        
        # Mantém compatibilidade com templates existentes
        if 'page_obj' in context:
            context['page_obj'] = context['page_obj']
        
        return context


class ServiceMixin:
    """
    Mixin para integração com a camada de serviço.
    
    Permite que views deleguem lógica de negócio para services.
    
    Attributes:
        service_class: Classe do serviço a ser utilizado
    """
    service_class = None
    
    def get_service(self):
        """
        Retorna uma instância do serviço.
        
        Returns:
            Instância do service_class
        """
        if self.service_class is None:
            raise ValueError("service_class deve ser definido")
        return self.service_class()


# =============================================================================
# PERMISSION MIXINS
# =============================================================================

class TechOnlyMixin(UserPassesTestMixin):
    """
    Mixin que permite acesso apenas para usuários técnicos.
    Redireciona para a página anterior com mensagem de erro se não for técnico.
    """
    
    def test_func(self):
        """Testa se o usuário é técnico."""
        return self.request.user.is_authenticated and self.request.user.is_tech
    
    def handle_no_permission(self):
        """Adiciona mensagem de erro e redireciona."""
        messages.add_message(
            self.request,
            constants.ERROR,
            "Você não tem permissão para acessar esta página!"
        )
        return redirect(self.request.META.get('HTTP_REFERER', '/'))
