# Próximos Passos - SISInfo V2

Roadmap e planejamento de desenvolvimento.

**Última atualização:** 2025-12-28

---

## ✅ Concluído

### Sistema de OCR (Supabase Edge Functions)
- [x] Migração para Supabase Edge Functions
- [x] Processamento assíncrono com callback
- [x] Detecção de imagem duplicada (hash MD5)
- [x] Rotação de múltiplas chaves Gemini
- [x] Deploy automático via GitHub Actions

### Sistema de Auditoria (MongoDB)
- [x] App `audit` com signals automáticos
- [x] Comandos de backup e limpeza

### Autenticação e Interface
- [x] Onboarding para primeiro login
- [x] Login apenas com email
- [x] Tema escuro (dark mode)
- [x] Notificações toast
- [x] Páginas de erro (400, 403, 404, 500)
- [x] Página de manutenção

### Infraestrutura
- [x] GitHub Actions para Edge Functions
- [x] Deploy automático na Vercel
- [x] Supabase Storage
- [x] Documentação completa
- [x] Integração Upstash na Vercel

---

## 📋 Backlog

### 🔴 Alta Prioridade - Upstash & Cache

#### Redis (Upstash)
- [ ] **Cache de Dashboard** - Stats, gráficos (TTL 5-10 min)
- [ ] **Cache de Listas** - Fornecedores, setores, materiais (TTL 30 min)
- [ ] **Rate Limiting** - Proteção de login e APIs
- [ ] **Session Store** - Sessões de usuário

#### QStash (Tarefas Agendadas)
- [ ] **Backup Automático + Google Drive** - Cron diário às 3h
- [ ] **Limpeza de OCRJobs** - Cron semanal
- [ ] **Fechamento de Laudos Antigos** - Cron mensal
- [ ] **Limpeza de Logs MongoDB** - Cron mensal

### 🟡 Média Prioridade - Interface

#### Dashboard - Novas Métricas
- [ ] Card: Notas Fiscais Pendentes de OCR
- [ ] Card: Entregas em Andamento
- [ ] Card: Materiais em Baixo Estoque
- [ ] Card: Status do OCR (Supabase)
- [ ] Gráfico: Evolução NFs por mês
- [ ] Gráfico: Top Fornecedores por valor

#### Novas Páginas
- [ ] **Página Sobre** - Versão, equipe, tecnologias, políticas
- [ ] **Central de Notificações** - Tela completa com histórico (design pronto)
- [ ] **Página de Ajuda/FAQ** - Documentação para usuários (design pronto)

### 🟢 Baixa Prioridade - Novos Apps

- [ ] **Sistema de Chamados TI** - Helpdesk interno
- [ ] **Inventário de Equipamentos** - Controle de patrimônio de TI

### Segurança
- [ ] Recuperação de senha por email
- [ ] Row Level Security (RLS)
- [ ] **Assinatura Digital de PDFs** - Laudos e entregas ([design](../features/design/assinatura_digital.md))

### Performance e Infraestrutura
- [ ] **Migração para UV** (gerenciador de pacotes Python)
- [ ] Otimizar queries N+1

### Testes
- [ ] Expandir cobertura de testes

---

## 🛠️ Upstash - Ferramentas Disponíveis

| Serviço | Uso no SISInfo | Status |
|---------|---------------|--------|
| **Redis** | Cache, rate limiting, sessions | 🔜 A implementar |
| **QStash** | Background jobs, cron, webhooks | 🔜 A implementar |
| **Workflow** | Orquestração multi-step (futuro) | ⏸️ Avaliar depois |
| **Vector** | Busca semântica (não aplicável) | ❌ Não usar |
| ~~Kafka~~ | ~~Streaming~~ | ⛔ Descontinuado |

> **Nota:** Kafka foi descontinuado em Set/2024. Suporte termina Mar/2025.

### Desenvolvimento Local

| Serviço | Produção | Desenvolvimento Local |
|---------|----------|----------------------|
| **PostgreSQL** | Supabase | `npx supabase start` |
| **Redis** | Upstash Redis | Docker (ver abaixo) |
| **QStash** | Upstash QStash | `npx @upstash/qstash-cli dev` |

#### QStash Local

```bash
# Iniciar emulador (em memória, dados perdidos ao reiniciar)
npx @upstash/qstash-cli dev

# Com porta personalizada
npx @upstash/qstash-cli dev --port=8081
```

Variáveis exibidas no console:
```bash
QSTASH_URL=http://localhost:8080
QSTASH_TOKEN=<token-local>
```

#### Redis Local (Docker)

```bash
# Redis simples
docker run -d --name redis-dev -p 6379:6379 redis:alpine

# Redis Stack (com UI RedisInsight em localhost:8001)
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

---

## 🎨 Designs Pendentes

Designs prontos na pasta `docs/features/design/`:

| Design | Descrição | Status |
|--------|-----------|--------|
| `assinatura_digital.md` | Assinatura digital de PDFs | Pendente |
| `ajuda_faq/` | Página de FAQ com acordeões | Pendente |

---

## 🗓️ Roadmap Atualizado

### Fase 1 - Cache & Automação (1-2 semanas)
1. Upstash Redis para cache de dashboard
2. Rate limiting no login
3. Página Sobre (estática, simples)

### Fase 2 - Background Jobs (2-3 semanas)
1. QStash para tarefas agendadas
2. Backup automático → Google Drive
3. Limpeza automática de OCRJobs e logs

### Fase 3 - Dashboard Melhorado (1 mês)
1. Novos cards de métricas
2. Gráficos adicionais
3. Indicadores em tempo real

### Fase 4 - Notificações (1-2 meses)
1. Central de Notificações (usar design pronto)
2. Realtime com Redis Pub/Sub

### Fase 5 - Novos Apps (2-3 meses)
1. Sistema de Chamados TI
2. Inventário de Equipamentos
3. Página de Ajuda/FAQ (usar design pronto)

### Fase 6 - Infraestrutura (contínuo)
1. Migração para UV
2. Otimização de queries
3. Expansão de testes

---

## 📊 Backup Automático - Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   QStash    │────▶│   Vercel    │────▶│   Django    │────▶│Google Drive │
│  (Cron 3h)  │     │  Endpoint   │     │  dumpdata   │     │   Upload    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Requisitos:**
- Google Cloud Project + Drive API
- Service Account + JSON Key
- Pasta compartilhada no Drive
- `google-api-python-client` + `google-auth`

---

## 🔧 Comandos de Manutenção

```bash
# Auditoria
python manage.py backup_audit_logs --days 30 --compress
python manage.py clean_audit_logs --days 90 --backup-first

# Banco de Dados
python manage.py backup_database
python manage.py diagnose_data

# OCR
python manage.py clean_ocr_jobs --days 7 --with-images

# Testes
python manage.py test --nomigrations
```

---

**Responsável:** Diretoria de TI  
**Contato:** ti@novohorizonte.sp.gov.br
