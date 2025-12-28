"""
Classes base para resultados de services.

Este módulo fornece classes padronizadas para retornos de services,
garantindo consistência na interface entre views e services.
"""
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ServiceResult:
    """
    Resultado padronizado para operações de service.
    
    Uso:
        # Em um service
        def create_item(data: dict) -> ServiceResult:
            try:
                item = Item.objects.create(**data)
                return ServiceResult(success=True, data=item, message="Item criado!")
            except Exception as e:
                return ServiceResult(success=False, error=str(e))
        
        # Na view
        result = MyService.create_item(data)
        if result.success:
            messages.success(request, result.message)
        else:
            messages.error(request, result.error)
    
    Attributes:
        success: Se a operação foi bem-sucedida
        data: Dados retornados (model, queryset, dict, etc)
        message: Mensagem de sucesso para exibir ao usuário
        error: Mensagem de erro em caso de falha
        errors: Lista de erros (para validação de múltiplos campos)
    """
    success: bool
    data: Any = None
    message: str = ""
    error: str = ""
    errors: list = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        """Verifica se há erros."""
        return bool(self.error or self.errors)
    
    @classmethod
    def ok(cls, data: Any = None, message: str = "Operação realizada com sucesso!"):
        """Atalho para resultado de sucesso."""
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def fail(cls, error: str, errors: list = None):
        """Atalho para resultado de erro."""
        return cls(success=False, error=error, errors=errors or [])


@dataclass
class PaginatedResult:
    """
    Resultado paginado para listagens.
    
    Attributes:
        items: Lista de itens da página atual
        total: Total de itens (sem paginação)
        page: Número da página atual
        per_page: Itens por página
        total_pages: Total de páginas
    """
    items: list
    total: int
    page: int = 1
    per_page: int = 20
    
    @property
    def total_pages(self) -> int:
        """Calcula total de páginas."""
        return (self.total + self.per_page - 1) // self.per_page
    
    @property
    def has_next(self) -> bool:
        """Verifica se há próxima página."""
        return self.page < self.total_pages
    
    @property
    def has_prev(self) -> bool:
        """Verifica se há página anterior."""
        return self.page > 1
