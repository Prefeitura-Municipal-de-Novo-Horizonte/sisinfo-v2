# TASK: Refatoração e Melhorias no App `reports`

## Objetivo
Refatorar e aplicar melhorias de código, legibilidade e boas práticas no app `reports`, que gerencia laudos técnicos, materiais associados e notas fiscais.

## Adequação do Nome do App
O nome `reports` é **apropriado** para este app, pois sua função principal é a gestão de laudos técnicos e funcionalidades relacionadas. Não há sugestão de alteração de nome.

## Plano de Ação

### 1. Modelos (`reports/models.py`)
- [ ] **`Report.save()`:** Isolar a lógica de geração do `number_report`. Criar uma função ou método de manager (ex: `Report.objects.create_report(...)`) que encapsule a criação do número e o salvamento do objeto, removendo essa responsabilidade do método `save()`.
- [ ] **`InterestRequestMaterial.save()`:** O método `save()` deste modelo altera o status do `Report` relacionado (`self.report.status = 2`). Isso cria um acoplamento indesejado. Considerar o uso de um `post_save` signal em `InterestRequestMaterial` para atualizar o `Report`, desacoplando os modelos.
- [ ] **`MaterialReport.save()`:** A lógica que busca o `unitary_price` do `Material` relacionado pode ser mantida, mas é um ponto a ser observado para garantir que o preço seja o correto no momento da criação do laudo.

### 2. Views (`reports/views.py`)
- [ ] **Refatorar para Class-Based Views (CBVs):** As views `reports`, `report_register`, `report_view`, e `report_update` são candidatos ideais para serem refatoradas para CBVs (`ListView`, `CreateView`, `DetailView`, `UpdateView`). Isso ajudará a:
    - Reduzir código repetitivo (ex: busca de objetos, renderização de templates).
    - Isolar a lógica de manipulação de `formsets` em métodos mais apropriados (ex: `get_context_data`, `post`).
    - Melhorar a legibilidade e manutenibilidade.
- [ ] **Permissões:** A lógica de permissão em `report_update` (`if request.user in [report.professional, report.pro_accountable]:`) pode ser movida para um mixin de permissão (`UserPassesTestMixin`) na `UpdateView` correspondente.
- [ ] **Cálculo de `total_price`:** A lógica de cálculo do preço total em `report_view` pode ser movida para um método ou `@property` no modelo `Report` (ex: `report.get_total_price()`), limpando a view.

### 3. Formulários (`reports/forms.py`)
- [ ] **Centralizar Estilo de Formulário:** Criar um `TailwindFormMixin` (conforme planejado em `TASK_utils.md`) e aplicá-lo a `ReportForm`, `ReportUpdateForm` e `MaterialReportForm` para remover a lógica de estilização repetitiva dos métodos `__init__`.
- [ ] **Simplificar `ReportForm.__init__()`:** A lógica de filtragem de `queryset` para os campos `professional` e `pro_accountable` pode ser simplificada. Em vez de fazer isso no `__init__`, a `queryset` pode ser passada dinamicamente na instanciação do formulário dentro da view.
- [ ] **`clean_employee`:** O método `clean_employee` está definido dentro da classe `Meta` em `ReportForm` e `ReportUpdateForm`. Ele deve ser movido para fora da `Meta`, diretamente para o escopo da classe do formulário.

### 4. Filtros (`reports/filters.py`)
- [ ] **Centralizar Estilo de Filtro:** Similar aos formulários, a estilização dos widgets do `ReportFilter` deve ser abstraída. Isso pode ser feito criando um `FilterForm` personalizado que aplique os estilos ou usando um mixin, alinhado com a solução de `TASK_utils.md`.

### 5. URLs (`reports/urls.py`)
- [ ] **Clareza na URL de exclusão:** A URL `path('report/material_report/<str:id>', ...)` funciona, mas não deixa claro a qual laudo o material pertence. Considerar uma estrutura mais explícita como `path('report/<slug:slug>/material/<int:pk>/delete', ...)` para melhorar a semântica e o controle de permissões.

## Status

- [x] Tarefa criada.
- [ ] Modelos revisados (isolação de lógica em `save`, uso de signals).
- [ ] Views refatoradas para CBVs.
- [ ] Lógica de permissão e cálculos movidos para mixins e modelos.
- [ ] Formulários revisados (centralização de estilos, simplificação de `__init__`, correção de `clean_*`).
- [ ] Filtros revisados (centralização de estilos).
- [ ] URLs revisadas (melhora semântica).
- [ ] Implementação concluída.
