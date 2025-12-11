"""
Mixins reutilizáveis para views do app bidding_procurement.
"""
from django.contrib import messages
from django.contrib.messages import constants
from django.core.paginator import Paginator


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
