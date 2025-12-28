# Style Guide - SISInfo V2

Padrões de código e convenções para o projeto SISInfo V2.

**Última atualização:** 2025-12-28

---

## Python

### Versão e Formatação

| Aspecto | Padrão |
|---------|--------|
| Python | 3.12+ |
| Formatador | - |
| Line length | 88 caracteres |
| Quotes | Duplas `"string"` |

### Imports

Ordenar imports em grupos separados por linha em branco:

```python
# 1. Standard library
import os
from datetime import datetime

# 2. Django
from django.db import models
from django.shortcuts import render

# 3. Third-party
from decouple import config

# 4. Local
from .models import MyModel
from .services import MyService
```

### Docstrings

```python
def calculate_total(items: list[Item], tax_rate: float = 0.1) -> Decimal:
    """
    Calcula o total com impostos.
    
    Args:
        items: Lista de itens para calcular
        tax_rate: Taxa de imposto (default: 10%)
    
    Returns:
        Valor total com impostos aplicados
    """
    ...
```

### Type Hints

Usar sempre em funções públicas:

```python
# ✅ Correto
def get_user(user_id: int) -> User | None:
    return User.objects.filter(id=user_id).first()

# ❌ Evitar
def get_user(user_id):
    return User.objects.filter(id=user_id).first()
```

---

## Django

### Estrutura de Apps

```
app_name/
├── __init__.py
├── admin.py           # Configurações do admin
├── apps.py            # AppConfig
├── forms.py           # Formulários Django
├── models.py          # Models (ou models/ se muitos)
├── services.py        # Lógica de negócio (ou services/)
├── signals.py         # Signals Django
├── urls.py            # URLs do app
├── views.py           # Views (ou views/ se muitas)
├── templates/
│   └── app_name/      # Templates específicos
├── management/
│   └── commands/      # Comandos customizados
└── tests/
    ├── __init__.py
    └── test_*.py      # Arquivos de teste
```

### Quando usar pasta vs arquivo único

| Cenário | Usar |
|---------|------|
| 1-3 views/services | Arquivo único (`views.py`) |
| 4+ views/services | Pasta com módulos (`views/`) |

### Models

```python
class Invoice(models.Model):
    """Nota fiscal recebida de fornecedor."""
    
    # Campos
    number = models.CharField("Número", max_length=50)
    date = models.DateField("Data")
    value = models.DecimalField("Valor", max_digits=10, decimal_places=2)
    
    # Relacionamentos
    supplier = models.ForeignKey(
        "bidding_supplier.Supplier",
        on_delete=models.PROTECT,
        verbose_name="Fornecedor"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Nota Fiscal"
        verbose_name_plural = "Notas Fiscais"
        ordering = ["-date"]
    
    def __str__(self):
        return f"NF {self.number} - {self.supplier}"
```

### Views (Function-Based)

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

@login_required
def invoice_detail(request, pk):
    """Exibe detalhes de uma nota fiscal."""
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, "fiscal/invoice_detail.html", {"invoice": invoice})
```

### Views (Class-Based)

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

class InvoiceListView(LoginRequiredMixin, ListView):
    """Lista de notas fiscais."""
    model = Invoice
    template_name = "fiscal/invoice_list.html"
    context_object_name = "invoices"
    paginate_by = 20
```

### Services

Encapsular lógica de negócio em services:

```python
# services.py
class InvoiceService:
    """Serviço para operações com notas fiscais."""
    
    @staticmethod
    def process_ocr(invoice_id: int) -> dict:
        """Processa OCR de uma nota fiscal."""
        invoice = Invoice.objects.get(id=invoice_id)
        # ... lógica
        return result
    
    @staticmethod
    def calculate_totals(invoice: Invoice) -> Decimal:
        """Calcula totais da nota fiscal."""
        return invoice.items.aggregate(total=Sum("value"))["total"] or Decimal("0")
```

### URLs

```python
from django.urls import path
from . import views

app_name = "fiscal"

urlpatterns = [
    path("", views.invoice_list, name="invoice_list"),
    path("<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("create/", views.invoice_create, name="invoice_create"),
]
```

---

## Utilitários do Core

### Mixins Centralizados

Usar mixins de `core/mixins.py` em vez de criar localmente:

```python
from core.mixins import (
    # Forms
    CapitalizeFieldMixin,
    TailwindFormMixin,
    
    # Filters
    TailwindFilterMixin,
    FilteredListMixin,
    
    # Views
    MessageMixin,
    FormsetMixin,
    PaginatedListMixin,
    ServiceMixin,
    
    # Permissions
    TechOnlyMixin,
)

class SupplierCreateView(LoginRequiredMixin, MessageMixin, CreateView):
    model = Supplier
    success_message = "Fornecedor criado com sucesso!"
```

### ServiceResult (Novo Padrão)

Para novos services, usar `ServiceResult` para retornos padronizados:

```python
from core.services import ServiceResult

class MyService:
    @staticmethod
    def create_item(data: dict) -> ServiceResult:
        try:
            item = Item.objects.create(**data)
            return ServiceResult.ok(data=item, message="Item criado!")
        except Exception as e:
            return ServiceResult.fail(error=str(e))

# Na view
result = MyService.create_item(data)
if result.success:
    messages.success(request, result.message)
else:
    messages.error(request, result.error)
```

### Constantes

Usar constantes de `core/constants.py`:

```python
from core.constants import (
    STATUS_ACTIVE_INACTIVE,
    INVOICE_STATUS,
    DELIVERY_STATUS,
)

class MyModel(models.Model):
    status = models.CharField(choices=STATUS_ACTIVE_INACTIVE, default="1")
```

---

## Templates

### Nomenclatura

| Tipo | Padrão |
|------|--------|
| Lista | `app/model_list.html` |
| Detalhe | `app/model_detail.html` |
| Formulário | `app/model_form.html` |
| Exclusão | `app/model_confirm_delete.html` |
| Parcial (include) | `app/_partial_name.html` |

### Estrutura de Template

```html
{% extends "_base.html" %}
{% load static %}

{% block title %}Título da Página{% endblock %}

{% block content %}
<div class="container mx-auto px-4">
    <h1 class="text-2xl font-bold mb-6 dark:text-white">
        Título
    </h1>
    
    <!-- Conteúdo -->
</div>
{% endblock %}

{% block script %}
<script>
    // JavaScript específico da página
</script>
{% endblock %}
```

---

## Testes

### Nomenclatura

```python
# tests/test_models.py
class InvoiceModelTest(TestCase):
    def test_str_returns_number_and_supplier(self):
        """__str__ retorna número e fornecedor."""
        ...
    
    def test_calculate_total_with_items(self):
        """calculate_total soma valores dos itens."""
        ...
```

### Estrutura de Testes

```python
from django.test import TestCase

class InvoiceServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Configuração executada uma vez para a classe."""
        cls.supplier = Supplier.objects.create(name="Test")
    
    def setUp(self):
        """Configuração executada antes de cada teste."""
        self.invoice = Invoice.objects.create(...)
    
    def test_process_ocr_success(self):
        """OCR processa imagem corretamente."""
        result = InvoiceService.process_ocr(self.invoice.id)
        self.assertTrue(result["success"])
```

---

## Git

### Commits (Conventional Commits)

```
<type>(<scope>): <description>

[optional body]
```

| Type | Uso |
|------|-----|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `style` | Formatação |
| `refactor` | Refatoração |
| `test` | Testes |
| `chore` | Manutenção |

**Exemplos:**
```
feat(fiscal): adiciona upload de imagem para OCR
fix(reports): corrige geração de PDF sem assinatura
docs: atualiza README com instruções de deploy
refactor(auth): extrai lógica de login para service
```

### Branches

| Tipo | Padrão |
|------|--------|
| Feature | `feature/nome-feature` |
| Fix | `fix/descricao-bug` |
| Refactor | `refactor/descricao` |
| Docs | `docs/descricao` |

---

**Responsável:** Diretoria de TI  
**Contato:** ti@novohorizonte.sp.gov.br
