# Próximos Passos - SISInfo V2

Documento de planejamento para futuras implementações e melhorias do sistema.

**Última atualização:** 2024-12-11

---

## ✅ Concluído Recentemente

### Sistema de Auditoria com MongoDB
- [x] App `audit` criado e configurado
- [x] Conexão MongoDB via pymongo implementada
- [x] Signals automáticos para CRUD
- [x] Middleware de auditoria
- [x] Comandos `backup_audit_logs` e `clean_audit_logs`
- [x] Integração com autenticação (login, logout, senha)

### Melhorias no Authenticate
- [x] Sistema de onboarding para primeiro login
- [x] Middleware de onboarding obrigatório
- [x] Remoção do campo username (login apenas com email)
- [x] Docstrings completas em models, forms e services
- [x] Métodos úteis: `can_access_admin()`, `get_role_display()`
- [x] Métodos de query: `get_active_users()`, `get_admins()`, `get_techs()`
- [x] Decorator `@admin_only` usando `can_access_admin()`

---

## 🔄 Sistema de Auditoria - Pendências

### Configuração e Testes
- [x] Instalar pymongo em produção (`pip install -r requirements.txt`)
- [x] Configurar string de conexão MongoDB Atlas no `.env` de produção
- [x] Testar conexão com MongoDB Atlas
- [x] Criar índices no MongoDB para performance (automático pelo pymongo ou manual)

### Manutenção
- [x] Configurar rotina de backup semanal de logs (via script/cron)
- [x] Configurar limpeza automática de logs (>90 dias) (via script/cron)
- [x] Adicionar mais modelos à lista `AUDITED_MODELS` conforme necessário (Sinais cobrem todos)

### Opcional
- [ ] Criar view de consulta de logs para administradores
- [ ] Configurar alertas para eventos suspeitos
- [ ] Dashboard de auditoria com estatísticas

---

## 🎨 Interface e UX

### Tom Select (Select2 Moderno)
- [ ] Instalar Tom Select via npm (`npm install tom-select`)
- [ ] Configurar no Tailwind config
- [ ] Criar template tag `as_select2` para Django
- [ ] Inicializar no template base
- [ ] Aplicar em formulários existentes:
  - [ ] Formulário de usuários
  - [ ] Formulário de licitações
  - [ ] Formulário de fornecedores
  - [ ] Formulário de materiais

**Benefícios:**
- ✅ Sem dependência de jQuery
- ✅ Busca, tags, multi-select
- ✅ Compatível com Tailwind CSS
- ✅ Mobile-friendly

### Outras Melhorias de UI
- [ ] Adicionar tema claro/escuro persistente
- [ ] Melhorar responsividade mobile
- [ ] Adicionar loading states
- [ ] Implementar notificações toast
- [ ] Adicionar breadcrumbs de navegação

---

## 🔐 Autenticação e Segurança

### Futuro
- [ ] Implementar rate limiting para login (django-ratelimit)
- [ ] Adicionar autenticação de dois fatores (2FA)
- [ ] Implementar recuperação de senha por email
- [ ] Adicionar histórico de senhas (evitar reutilização)
- [ ] Política de expiração de senha

---

## 📊 Sistema de Serviços (Helpdesk)

### Planejamento
- [ ] Criar app `services` para sistema de tickets
- [ ] Modelo de Ticket (título, descrição, prioridade, status)
- [ ] Modelo de Categoria de Serviço
- [ ] Sistema de atribuição de tickets
- [ ] Notificações por email
- [ ] Dashboard de tickets
- [ ] Relatórios de SLA
- [ ] Adicionar modelos de serviço à lista `AUDITED_MODELS`

---

## 📈 Melhorias Gerais

### Performance
- [ ] Implementar cache (Redis/Memcached)
- [ ] Otimizar queries N+1 com `select_related` e `prefetch_related`
- [ ] Adicionar paginação em listagens grandes
- [ ] Minificar e comprimir assets estáticos

### Testes
- [ ] Expandir cobertura de testes unitários
- [ ] Adicionar testes de integração
- [ ] Configurar CI/CD (GitHub Actions)
- [ ] Testes de performance

### Documentação
- [ ] Criar documentação de API (se necessário)
- [ ] Documentar fluxos de trabalho principais
- [ ] Criar guia de contribuição detalhado
- [ ] Adicionar diagramas de arquitetura

---

## 📦 Infraestrutura

### DevOps
- [ ] Configurar ambiente de staging
- [ ] Implementar deploy automatizado
- [ ] Configurar backups automáticos do PostgreSQL
- [ ] Monitoramento de erros (Sentry)
- [ ] Monitoramento de performance (New Relic/DataDog)

### Segurança
- [ ] Implementar HTTPS obrigatório
- [ ] Configurar Content Security Policy (CSP)
- [ ] Adicionar proteção contra CSRF em AJAX
- [ ] Implementar rate limiting global
- [ ] Auditoria de segurança

---

## 📝 Compliance e Auditoria

### LGPD
- [ ] Implementar termo de consentimento
- [ ] Adicionar funcionalidade de exportação de dados do usuário
- [ ] Implementar exclusão de dados (direito ao esquecimento)
- [ ] Criar política de privacidade
- [ ] Registro de tratamento de dados

### Auditoria Pública
- [ ] Relatórios de acesso para auditoria interna
- [ ] Logs de alterações críticas (já implementado ✅)
- [ ] Relatórios de conformidade
- [ ] Documentação de processos

---

## 🔧 Manutenção

### Rotinas Recomendadas
- **Semanal**: Backup do MongoDB (logs de auditoria)
- **Mensal**: Limpeza de logs antigos (>90 dias)
- **Trimestral**: Revisão de usuários inativos
- **Mensal**: Atualização de dependências

### Comandos Úteis

#### Auditoria
```bash
# Backup de logs
python manage.py backup_audit_logs
python manage.py backup_audit_logs --days 30 --compress

# Limpeza de logs
python manage.py clean_audit_logs --days 90 --dry-run
python manage.py clean_audit_logs --days 90 --backup-first
```

#### Banco de Dados
```bash
# Backup do PostgreSQL
python manage.py backup_database

# Diagnóstico de dados
python manage.py diagnose_data

# Limpeza de duplicatas
python manage.py clean_duplicate_biddings
python manage.py clean_duplicate_materials
python manage.py consolidate_suppliers
```

---

## 📅 Roadmap Sugerido

### Curto Prazo (1-2 meses)
1. ✅ ~~Finalizar sistema de auditoria (MongoDB)~~
2. ✅ ~~Implementar sistema de onboarding~~
3. 🔄 Configurar MongoDB em produção
4. 🔄 Implementar Tom Select
5. Melhorar testes e cobertura

### Médio Prazo (3-6 meses)
1. Implementar sistema de helpdesk/serviços
2. Implementar 2FA
3. Adicionar cache e otimizações
4. Configurar CI/CD
5. Implementar monitoramento

### Longo Prazo (6-12 meses)
1. Compliance LGPD completo
2. API pública (se necessário)
3. Mobile app (se necessário)
4. Integração com outros sistemas municipais
5. Dashboard analytics avançado

---

## 📚 Recursos e Referências

### Documentação Técnica
- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [MongoDB Atlas](https://www.mongodb.com/docs/atlas/)
- [Tom Select](https://tom-select.js.org/)

### Ferramentas Úteis
- **Linting**: djlint, prettier
- **Testes**: pytest-django
- **Monitoramento**: Sentry, New Relic
- **Deploy**: Docker, GitHub Actions

---

**Responsável:** Equipe de TI - Prefeitura de Novo Horizonte  
**Contato:** ti@novohorizonte.sp.gov.br
