# Roadmap Unificado - SISInfo V2

Ordem de execução priorizada consolidando todas as documentações do projeto.

**Última atualização:** 2025-12-29

---

## 📋 Visão Geral das Fases

| Fase | Foco | Duração | Status |
|------|------|---------|--------|
| 0 | Fundação (Sentry + Dependabot) | 1-2 dias | ✅ Concluído |
| 1 | Cache & Segurança (Redis + Rate Limit) | 1-2 semanas | ✅ Concluído |
| 2 | Automação (QStash + Google Drive) | 2-3 semanas | 🔜 Próximo |
| 3 | Qualidade (Testes + CI) | 1-2 semanas | ⏳ Aguardando |
| 4 | Dashboard & Interface | 1 mês | ⏳ Aguardando |
| 5 | Features Avançadas (Assinatura Digital) | 1-2 meses | ⏳ Aguardando |
| 6 | Novos Apps | 2-3 meses | ⏳ Aguardando |

---

## Fase 0 - Fundação ✅ Concluído

> **Objetivo:** Ganhar visibilidade de erros e manter dependências seguras.

### 0.1 Sentry (Error Tracking)
- [x] Criar conta no Sentry (free tier)
- [x] Instalar `sentry-sdk[django]`
- [x] Configurar em `production.py` e `sentry.py`
- [x] Testar com erro proposital

### 0.2 Dependabot
- [x] Criar `.github/dependabot.yml`
- [x] Habilitar alertas de segurança

**Concluído em:** 2025-12-29

---

## Fase 1 - Cache & Segurança ✅ Concluído

> **Objetivo:** Proteger APIs e melhorar performance com Upstash Redis.

### 1.1 Upstash Redis - Setup
- [x] Criar conta Upstash (free tier)
- [x] Obter `UPSTASH_REDIS_REST_URL` e `UPSTASH_REDIS_REST_TOKEN`
- [x] Criar `core/cache.py` (wrapper dual dev/prod)
- [x] Configurar variáveis no `.env`

### 1.2 Rate Limiting
- [x] Rate limit no login (5/min por IP)
- [ ] Rate limit nas APIs críticas (OCR, PDFs) - *baixa prioridade*

### 1.3 Cache de Dashboard
- [x] Cache de estatísticas (TTL 5 min)
- [x] Cache de gráficos (TTL 30 min)

### 1.4 Cache de Listas
- [x] Fornecedores (TTL 30 min)
- [x] Setores/Diretorias (TTL 30 min)
- [x] Materiais (TTL 30 min)
- [x] Licitações (TTL 30 min)

### 1.5 Invalidação Automática
- [x] Signals para invalidar cache ao criar/editar/deletar

### 1.6 Session Store
- [x] ~~Migrar sessões para Redis~~ - Descartado (não recomendado para serverless/Vercel)

**Concluído em:** 2025-12-29

**Esforço real:** ~2 horas

---

## Fase 2 - Automação (2-3 semanas)

> **Objetivo:** Backup automático e limpeza de dados com QStash.

### 2.1 Google Drive API
- [ ] Criar projeto no Google Cloud
- [ ] Habilitar Drive API
- [ ] Criar Service Account
- [ ] Gerar JSON key
- [ ] Criar pasta compartilhada

### 2.2 Integração Django + Drive
- [ ] Instalar `google-api-python-client`
- [ ] Serviço de upload
- [ ] Testar upload manual

### 2.3 QStash - Setup
- [ ] Criar conta QStash (free tier)
- [ ] Configurar webhook URL
- [ ] Testar endpoint local

### 2.4 Backup Automático
- [ ] Endpoint `/api/webhooks/backup/`
- [ ] Cron QStash (diário 3h)
- [ ] Upload para Google Drive
- [ ] Notificação de sucesso/erro

**Docs:** [PROXIMOS_PASSOS.md](PROXIMOS_PASSOS.md#backup-automático---arquitetura)

### 2.5 Limpezas Automáticas
- [ ] Limpeza OCRJobs (semanal)
- [ ] Fechamento de laudos antigos (mensal)
- [ ] Limpeza logs MongoDB (mensal)

**Esforço:** ~2-3 semanas

---

## Fase 3 - Qualidade (1-2 semanas)

> **Objetivo:** Melhorar cobertura de testes e CI.

### 3.1 GitHub Actions - Testes
- [ ] Criar `.github/workflows/test.yml`
- [ ] Rodar testes em PRs
- [ ] Falhar merge se testes falharem

### 3.2 Expandir Testes
- [ ] Testes de autenticação
- [ ] Testes de laudos (CRUD)
- [ ] Testes de entregas (CRUD)
- [ ] Testes de permissões

### 3.3 Health Check Completo
- [ ] Endpoint `/api/health/`
- [ ] Verificar banco PostgreSQL
- [ ] Verificar MongoDB
- [ ] Verificar Supabase Storage
- [ ] Verificar Redis (quando implementado)

**Docs:** [ANALISE_PRODUCAO.md](ANALISE_PRODUCAO.md#5-testes-automatizados)

**Esforço:** ~1-2 semanas

---

## Fase 4 - Dashboard & Interface (1 mês)

> **Objetivo:** Melhorar dashboard e criar páginas pendentes.

### 4.1 Novos Cards
- [ ] Notas Fiscais Pendentes de OCR
- [ ] Entregas em Andamento
- [ ] Materiais em Baixo Estoque
- [ ] Status do OCR

### 4.2 Novos Gráficos
- [ ] Evolução NFs por mês
- [ ] Top Fornecedores por valor

### 4.3 Interface de Logs de Auditoria
- [ ] Página `/admin/audit/` para visualizar logs
- [ ] Filtros por usuário, ação, data
- [ ] Exportar logs (CSV/JSON)
- [ ] Paginação

### 4.4 Página Sobre
- [ ] Versão do sistema
- [ ] Equipe
- [ ] Tecnologias usadas
- [ ] Políticas

### 4.5 (Opcional) Central de Notificações
- [ ] Usar design existente
- [ ] Backend de notificações
- [ ] Realtime com Redis Pub/Sub

**Docs:** [PROXIMOS_PASSOS.md](PROXIMOS_PASSOS.md#dashboard---novas-métricas)

**Esforço:** ~1 mês

---

## Fase 5 - Features Avançadas (1-2 meses)

> **Objetivo:** Implementar assinatura digital e recuperação de senha.

### 5.1 Assinatura Digital de PDFs
- [ ] Gerar certificado autoassinado
- [ ] Integrar pyHanko
- [ ] Serviço de assinatura via QStash
- [ ] Upload PDF assinado → Google Drive
- [ ] UI de assinatura (botão, modal)
- [ ] Bloqueio após assinatura
- [ ] Permissões específicas

**Docs:** [assinatura_digital.md](../features/design/assinatura_digital.md)

### 5.2 Recuperação de Senha
- [ ] Formulário "Esqueci minha senha"
- [ ] Email com link de reset
- [ ] Página de redefinição
- [ ] Expiração do token

**Esforço:** ~1-2 meses

---

## Fase 6 - Novos Apps (2-3 meses)

> **Objetivo:** Expandir o sistema com novos módulos.

### 6.1 Sistema de Chamados TI
- [ ] Model de Chamado
- [ ] Categories/Prioridades
- [ ] Workflow de atendimento
- [ ] Dashboard de chamados

### 6.2 Inventário de Equipamentos
- [ ] Model de Equipamento
- [ ] QR Code para identificação
- [ ] Histórico de movimentação
- [ ] Relatórios

### 6.3 Página de Ajuda/FAQ
- [ ] Usar design existente
- [ ] Conteúdo das FAQs
- [ ] Sistema de busca

**Esforço:** ~2-3 meses

---

## 📊 Métricas de Progresso

| Métrica | Atual | Meta |
|---------|-------|------|
| Error tracking | ❌ | Sentry ativo |
| Rate limiting | ❌ | Login protegido |
| Cache | ❌ | Dashboard cacheado |
| Backup automático | ❌ | Diário às 3h |
| Cobertura de testes | ~20% | >50% |
| Health check | Básico | Completo |

---

## 🔗 Documentos Relacionados

| Documento | Descrição |
|-----------|-----------|
| [PROXIMOS_PASSOS.md](PROXIMOS_PASSOS.md) | Backlog detalhado |
| [ANALISE_PRODUCAO.md](ANALISE_PRODUCAO.md) | Análise de gaps de produção |
| [assinatura_digital.md](../features/design/assinatura_digital.md) | Design de assinatura digital |
| [GEMINI.md](../../GEMINI.md) | Contexto para IA |

---

## ⚡ Atalho: Começar Agora

Se quiser começar imediatamente, a **Fase 0** (Sentry + Dependabot) leva apenas **2-4 horas** e dá visibilidade imediata de problemas em produção.

```bash
# Instalar Sentry
pip install sentry-sdk[django]

# Adicionar ao requirements.txt
echo "sentry-sdk[django]" >> requirements.txt
```

---

**Responsável:** Diretoria de TI  
**Contato:** ti@novohorizonte.sp.gov.br
