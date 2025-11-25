# TASK: Limpeza de Código e Arquivos Legados

## Objetivo
Remover arquivos de configuração antigos e código comentado/morto para manter o projeto limpo e evitar confusão.

## Plano de Ação
- [ ] **Remover `core/settings.py`**: O projeto já utiliza `core/settings/` (base, development, production). O arquivo antigo deve ser removido.
- [ ] **Remover Código Comentado**: Varrer o projeto em busca de blocos de código comentado que não são mais necessários (ex: antigas configurações, views desativadas).
- [ ] **Remover Arquivos de Backup**: Verificar se há arquivos `.bak` ou `.json` de backup antigos que podem ser arquivados ou excluídos.

## Status
- [x] Tarefa criada.
- [x] `core/settings.py` removido.
- [ ] Código comentado removido.
- [ ] Arquivos de backup limpos.
- [ ] Implementação concluída.
