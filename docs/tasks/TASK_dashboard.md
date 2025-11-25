# TASK: Refatoração e Reestruturação do App `dashboard`

## Objetivo
Reestruturar o app `dashboard` dividindo-o em apps menores e mais coesos, melhorando a modularidade, manutenibilidade e escalabilidade do projeto. Além disso, aplicar melhorias de código e boas práticas nas funcionalidades existentes.

## Adequação do Nome do App
O nome `dashboard` é **inapropriado** para o escopo atual deste app. Ele contém lógica de negócio central e modelos para "Setores e Diretorias" e "Licitação e Suprimentos", que são domínios distintos. Um dashboard deve ser uma interface de agregação de informações, não um contêiner para funcionalidades primárias.

## Plano de Ação (Reestruturação e Refatoração)

### 1. Divisão do App `dashboard`
O app `dashboard` será dividido em três apps mais específicos:

#### 1.1. Novo App: `organizational_structure` (ou `sectors_directions`)
- [ ] **Propósito:** Gerenciar os modelos e funcionalidades relacionadas a Diretorias e Setores.
- [ ] **Modelos:** Mover `AbsctactDirectionSector`, `Direction`, `Sector` para `organizational_structure/models.py`.
- [ ] **Views:** Mover `directions`, `direction_detail`, `direction_update`, `direction_delete`, `sectors`, `sector_detail`, `sector_update`, `sector_delete` para `organizational_structure/views.py`.
- [ ] **Forms:** Mover `DirectionForm`, `SectorForm` para `organizational_structure/forms.py`.
- [ ] **Filters:** Mover `DirectionFilter`, `SectorFilter` para `organizational_structure/filters.py`.
- [ ] **Templates:** Mover o conteúdo de `dashboard/templates/setores/` para `organizational_structure/templates/organizational_structure/`.
- [ ] **URLs:** Criar `organizational_structure/urls.py` com as URLs correspondentes.

#### 1.2. Novo App: `bidding_procurement` (ou `bidding`)
- [x] **Propósito:** Gerenciar os modelos e funcionalidades relacionadas a Licitações e Materiais.
- [x] **Modelos:** Mover `AbsBiddingMaterial`, `Bidding`, `Material` para `bidding_procurement/models.py`.
- [x] **Views:** Mover `biddings`, `bidding_detail`, `bidding_update`, `bidding_delete`, `materials`, `material_detail`, `material_update`, `material_delete` para `bidding_procurement/views.py`.
- [x] **Forms:** Mover `BiddingForm`, `MaterialForm` para `bidding_procurement/forms.py`.
- [x] **Filters:** Mover `BiddingFilter`, `MaterialFilter` para `bidding_procurement/filters.py`.
- [x] **Templates:** Mover o conteúdo de `dashboard/templates/licitacao/` para `bidding_procurement/templates/bidding_procurement/`.
- [x] **URLs:** Criar `bidding_procurement/urls.py` com as URLs correspondentes.

#### 1.3. App `dashboard` (Repurposed)
- [x] **Propósito:** Servir como uma página de entrada central que agrega e exibe métricas e links importantes de outros apps.
- [x] **Views:** Manter apenas a view `index` em `dashboard/views.py`. Esta view será atualizada para importar dados dos novos apps `organizational_structure`, `bidding_procurement` e `reports`.
- [x] **Templates:** Manter `dashboard/templates/index.html`.
- [x] **Remoção:** Remover todos os outros arquivos e diretórios que foram movidos para os novos apps.

### 2. Melhorias Gerais (Aplicáveis aos Novos Apps)

#### 2.1. Modelos
- [x] **`Bidding.save` method:** Refatorar a lógica que atualiza o status do `Material`. Considerar o uso de Django signals (ex: `post_save` para `Bidding`) ou uma função de serviço dedicada para desacoplar essa lógica do método `save` do modelo.
- [x] **`Material.save` method:** Revisar a geração de slug para `Material` para garantir unicidade e legibilidade. Considerar uma abordagem mais simples ou um utilitário robusto de geração de slug.
- [x] **`Sector.direction` `on_delete`:** Reavaliar `models.DO_NOTHING`. Considerar `models.SET_NULL` (com `null=True`) ou `models.CASCADE` baseado nas regras de negócio para o que deve acontecer quando uma `Direction` é excluída.

#### 2.2. Views
- [x] **Funções Auxiliares (`extract_update_form_...`):** São repetitivas. Considerar um mixin genérico para `ModelForm` views que lida com salvamento e redirecionamento, ou uma função utilitária que recebe o formulário e a requisição como argumentos.

#### 2.3. Formulários
- [x] **`extract_from_clean` duplication:** Centralizar o método `extract_from_clean` (para capitalizar nomes) em um módulo de utilidade compartilhado (ex: `core/utils` ou um novo app `utils`) e fazer com que todos os formulários o herdem.
- [x] **`MaterialForm.Meta.clean_name` bug:** Mover o método `clean_name` da classe `Meta` para a classe `MaterialForm`.
- [x] **Estilo de Formulário:** Centralizar a lógica de estilo do Tailwind CSS em um mixin compartilhado (como `TailwindFormMixin` do app `authenticate`) e aplicá-lo a todos os formulários nos novos apps `organizational_structure` e `bidding_procurement`.

#### 2.4. Filters
- [x] **Estilo de Filtro:** Centralizar o estilo do Tailwind CSS para widgets `django-filters`. Isso pode ser feito criando classes de widget personalizadas que herdam de `TextInput` e aplicam os estilos, ou usando um formulário de filtro personalizado que aplica estilos em seu `__init__`.

#### 2.5. URLs
- [x] **Redundância de ID em URLs de exclusão:** Para operações de exclusão (`direction_delete`, `sector_delete`, `bidding_delete`, `material_delete`), se o `slug` for garantido como único, o `id` na URL pode ser redundante. Simplificar URLs para usar apenas `slug` se possível.

## Status

- [x] Tarefa criada.
- [/] Divisão do App `dashboard` iniciada (criar apps `organizational_structure` e `bidding_procurement`).
    - [x] App `organizational_structure` criado.
    - [x] Models `Direction` e `Sector` movidos.
- [x] Melhorias Gerais implementadas (refatoração de modelos, views, formulários, filtros, templates, URLs, utilitários compartilhados).
- [x] Implementação concluída.
