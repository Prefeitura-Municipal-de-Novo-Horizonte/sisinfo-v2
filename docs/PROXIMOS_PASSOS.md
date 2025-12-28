# Próximos Passos - SISInfo V2

Roadmap e planejamento de desenvolvimento.

**Última atualização:** 2024-12-27

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

---

## 📋 Backlog

### Supabase - Alta Prioridade
- [ ] **Cron Jobs** - Tarefas agendadas (limpeza OCR, backup logs)
- [ ] **Realtime** - Notificações em tempo real
- [ ] **Central de Notificações** - Tela completa com histórico (design pronto)

### Novos Apps
- [ ] **Sistema de Chamados TI** - Helpdesk interno
- [ ] **Inventário de Equipamentos** - Controle de patrimônio de TI
- [ ] **Página de Ajuda/FAQ** - Documentação para usuários (design pronto)

### Interface e UX
- [ ] Tom Select para selects (busca e tags)
- [ ] Melhorar responsividade mobile
- [ ] Dashboard com métricas em tempo real

### Segurança
- [ ] Rate limiting para login
- [ ] Recuperação de senha por email
- [ ] Row Level Security (RLS)

### Performance e Infraestrutura
- [ ] Cache com Redis/Upstash
- [ ] **Migração para UV** (gerenciador de pacotes Python)
- [ ] Otimizar queries N+1

### Testes
- [ ] Expandir cobertura de testes

---

## 🎨 Designs Pendentes

Designs prontos na pasta `docs/design/`:

| Design | Descrição | Status |
|--------|-----------|--------|
| `central_de_notificações` | Tela de notificações com histórico | Pendente |
| `ajuda_/_faq` | Página de FAQ com acordeões | Pendente |

---

## 🗓️ Roadmap

### Fase 1 - Automação (1-2 semanas)
1. Supabase Cron Jobs para manutenção automática
2. Supabase Realtime básico

### Fase 2 - Notificações (1 mês)
1. Central de Notificações (usar design pronto)
2. Dashboard com métricas em tempo real

### Fase 3 - Novos Apps (2-3 meses)
1. Sistema de Chamados TI
2. Inventário de Equipamentos
3. Página de Ajuda/FAQ (usar design pronto)

### Fase 4 - Infraestrutura (contínuo)
1. Migração para UV
2. Cache Redis/Upstash
3. Rate limiting

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
