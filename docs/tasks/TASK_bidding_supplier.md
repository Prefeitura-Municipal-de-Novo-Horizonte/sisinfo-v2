# TASK: Refatoração e Melhorias no App `bidding_supplier`

## Objetivo
Refatorar e aplicar melhorias de código, legibilidade e boas práticas no app `bidding_supplier`, que gerencia fornecedores e seus contatos.

## Adequação do Nome do App
O nome `bidding_supplier` é **aceitável**, mas pode ser mais preciso. Atualmente, o app foca na gestão de dados de fornecedores. A conexão com o modelo `Material` no `supplier_detail` sugere um vínculo com processos de licitação/aquisição. Se a funcionalidade de "bidding" (ex: gestão de lances, editais) for tratada em outro app (como `dashboard`) e este app servir como fonte de dados de fornecedores para isso, o nome é justificado. Caso contrário, `suppliers` ou `supplier_management` seriam mais precisos. Por ora, manteremos o nome, assumindo o contexto mais amplo de "bidding" implícito ou tratado em outro local.

## Plano de Ação

### 1. Formulários (`bidding_supplier/forms.py`)
- [ ] **Centralizar Estilo de Formulário:** Implementar um mixin (similar ao `TailwindFormMixin` do app `authenticate`) para aplicar classes CSS comuns do Tailwind aos campos de formulário em `SupplierForm` e `ContactForm`, reduzindo a duplicação de código. Para simplificar, o mixin será criado dentro deste app, mas futuramente pode ser movido para um módulo de utilidade compartilhado (`core/utils` ou um novo app `utils`).

### 2. URLs (`bidding_supplier/urls.py`)
- [ ] **Redundância de ID em `supplier_delete`:** A URL `supplier_delete` utiliza tanto `slug` quanto `id`. Se o `slug` for garantido como único, o `id` pode ser redundante. Avaliar se o `id` é estritamente necessário para a operação de exclusão ou se o `slug` sozinho é suficiente. Por ora, manteremos como está, mas será notado para potencial simplificação.

## Status

- [x] Tarefa criada.
- [ ] Formulários revisados (centralização de estilos, criação/aplicação de mixin).
- [ ] URLs revisadas (simplificação de parâmetros redundantes).
- [ ] Implementação concluída.
