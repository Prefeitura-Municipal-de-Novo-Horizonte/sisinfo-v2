# Próximos Passos - SISInfo V2

Documento de planejamento para futuras implementações e melhorias do sistema.

---

## 🔄 Sistema de Auditoria

### Pendente
- [ ] Instalar pymongo (`pip install -r requirements.txt`)
- [ ] Testar conexão com MongoDB Atlas
- [ ] Criar índices no MongoDB para performance
- [ ] Adicionar mais modelos à lista `AUDITED_MODELS` conforme necessário
- [ ] Criar view de consulta de logs (opcional)
- [ ] Configurar alertas para eventos suspeitos (opcional)

### Comandos Disponíveis
```bash
# Backup de logs
python manage.py backup_audit_logs
python manage.py backup_audit_logs --days 30 --compress

# Limpeza de logs
python manage.py clean_audit_logs --days 90 --dry-run
python manage.py clean_audit_logs --days 90 --backup-first
```

---

## 🔐 Autenticação e Segurança

### Concluído ✅
- [x] Sistema de onboarding para primeiro login
- [x] Middleware de onboarding obrigatório
- [x] Remoção do campo username (usar email)
- [x] Melhorias de código e documentação
- [x] Decorator `@admin_only` usando `can_access_admin()`

### Futuro
- [ ] Implementar rate limiting para login (django-ratelimit)
- [ ] Adicionar autenticação de dois fatores (2FA)
- [ ] Implementar recuperação de senha por email
- [ ] Adicionar histórico de senhas (evitar reutilização)

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

### Auditoria
- [ ] Adicionar modelos de serviço à lista `AUDITED_MODELS`

---

## 📈 Melhorias Gerais

### Performance
- [ ] Implementar cache (Redis/Memcached)
- [ ] Otimizar queries N+1 com `select_related` e `prefetch_related`
- [ ] Adicionar paginação em listagens grandes

### Testes
- [ ] Expandir cobertura de testes unitários
- [ ] Adicionar testes de integração
- [ ] Configurar CI/CD (GitHub Actions)

### Documentação
- [ ] Criar documentação de API (se necessário)
- [ ] Documentar fluxos de trabalho principais
- [ ] Criar guia de contribuição

---

## 🎨 Interface e UX

### Melhorias
- [ ] Adicionar tema claro/escuro persistente
- [ ] Melhorar responsividade mobile
- [ ] Adicionar loading states
- [ ] Implementar notificações toast
- [ ] Adicionar breadcrumbs de navegação

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

---

## 📝 Compliance e Auditoria

### LGPD
- [ ] Implementar termo de consentimento
- [ ] Adicionar funcionalidade de exportação de dados do usuário
- [ ] Implementar exclusão de dados (direito ao esquecimento)
- [ ] Criar política de privacidade

### Auditoria Pública
- [ ] Relatórios de acesso para auditoria interna
- [ ] Logs de alterações críticas
- [ ] Relatórios de conformidade

---

## 🔧 Manutenção

### Rotinas
- [ ] Backup semanal do MongoDB (logs)
- [ ] Limpeza mensal de logs antigos (>90 dias)
- [ ] Revisão trimestral de usuários inativos
- [ ] Atualização de dependências (mensal)

### Comandos Úteis
```bash
# Backup do PostgreSQL
python manage.py backup_database

# Diagnóstico de dados
python manage.py diagnose_data

# Limpeza de duplicatas
python manage.py clean_duplicate_biddings
python manage.py clean_duplicate_materials
```

---

## 📅 Roadmap Sugerido

### Curto Prazo (1-2 meses)
1. Finalizar sistema de auditoria (MongoDB)
2. Implementar sistema de serviços/helpdesk
3. Melhorar testes e cobertura

### Médio Prazo (3-6 meses)
1. Implementar 2FA
2. Adicionar cache e otimizações
3. Configurar CI/CD
4. Implementar monitoramento

### Longo Prazo (6-12 meses)
1. Compliance LGPD completo
2. API pública (se necessário)
3. Mobile app (se necessário)
4. Integração com outros sistemas municipais

---

**Última atualização:** 2024-12-11  
**Responsável:** Equipe de TI - Prefeitura de Novo Horizonte
