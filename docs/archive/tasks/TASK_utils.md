# TASK: Criação de Utilitários Compartilhados (Mixins, Helpers, etc)

## Objetivo
Centralizar lógica e estilos comuns (ex: TailwindFormMixin, helpers de template, funções utilitárias) em um módulo compartilhado para uso em todos os apps.

## Plano de Ação
- [ ] Criar diretório/módulo de utilitários compartilhados (`core/utils` ou novo app `utils`).
- [ ] Implementar mixins para formulários (ex: TailwindFormMixin).
- [ ] Implementar helpers/tags para templates (ex: renderização de campos).
- [ ] Implementar funções utilitárias para views, filtros, etc.
- [ ] Refatorar apps para utilizar os utilitários compartilhados.
- [ ] Testar funcionamento e integração.

## Status
- [x] Tarefa criada.
- [x] Estrutura inicial criada (`core/mixins.py`, `core/templatetags`).
- [x] Mixins implementados (`TailwindFormMixin`, `CapitalizeFieldMixin`).
- [x] Helpers/tags implementados (`ui_tags.py`).
- [x] Funções utilitárias implementadas.
- [x] Apps refatorados para uso dos utilitários.
- [x] Testes realizados.
- [x] Implementação concluída.
