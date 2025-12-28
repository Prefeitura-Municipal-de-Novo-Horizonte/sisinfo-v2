# GEMINI.MD: Contexto do Projeto para IA

Este documento fornece contexto essencial para modelos de IA que interagem com o projeto SISInfo V2.

---

## Projeto

**SISInfo V2** - Sistema Integrado de Gestão da Diretoria de TI  
**Domínio:** Gestão Pública Municipal / Tecnologia da Informação  
**Organização:** Prefeitura Municipal de Novo Horizonte/SP

---

## Stack Tecnológico

| Camada | Tecnologias |
|--------|-------------|
| **Backend** | Python 3.12, Django 5.2 |
| **Frontend** | Tailwind CSS 3.4, Alpine.js 3.13, HTMX 1.9 |
| **Banco Principal** | PostgreSQL (Supabase) |
| **Logs de Auditoria** | MongoDB Atlas |
| **Cache/Queue** | Upstash (Redis + QStash) |
| **PDF** | Browserless.io + Playwright |
| **Serverless** | Supabase Edge Functions (Deno) |
| **Storage** | Supabase Storage |
| **Deploy** | Vercel |

---

## Estrutura de Apps Django

| App | Descrição |
|-----|-----------|
| `authenticate` | Autenticação, usuários, onboarding |
| `audit` | Sistema de auditoria (MongoDB) |
| `bidding_procurement` | Licitações e materiais |
| `bidding_supplier` | Fornecedores |
| `dashboard` | Painel principal |
| `fiscal` | Notas fiscais, entregas, estoque, OCR |
| `organizational_structure` | Diretorias e setores |
| `reports` | Laudos técnicos e geração de PDFs |
| `core` | Configurações globais |

---

## Convenções de Código

### Python
- **Estilo:** PEP 8
- **Nomenclatura:** `snake_case` (variáveis/funções), `PascalCase` (classes)
- **Docstrings:** Obrigatórias em classes e métodos públicos
- **Type hints:** Recomendados

### JavaScript/CSS
- **Formatação:** Prettier com `prettier-plugin-tailwindcss`

### Templates Django
- **Linting:** djlint

### Commits
- **Obrigatório:** [Conventional Commits](https://www.conventionalcommits.org/)
- **Formato:** `<tipo>(<escopo>): <descrição>`
- **Tipos:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

---

## Padrão Arquitetural

O projeto usa **Service Layer** sobre o MVT do Django:

```
Models (dados) → Services (lógica) → Views (HTTP) → Templates (UI)
```

---

## Comandos de Management Importantes

### Manutenção de Dados
```bash
python manage.py diagnose_data          # Diagnóstico completo do banco
python manage.py consolidate_suppliers  # Consolida fornecedores duplicados
python manage.py close_stale_reports    # Fecha laudos pendentes antigos
```

### Auditoria (MongoDB)
```bash
python manage.py backup_audit_logs      # Backup de logs
python manage.py clean_audit_logs       # Limpeza de logs antigos
```

### OCR
```bash
python manage.py clean_ocr_jobs         # Limpa jobs de OCR órfãos
python manage.py clean_orphan_images    # Remove imagens órfãs
```

### Backup
```bash
python manage.py backup_database        # Backup do PostgreSQL
python manage.py restore_backup         # Restaura backup
```

---

## Arquivos Chave

| Arquivo | Propósito |
|---------|-----------|
| `core/settings/base.py` | Configurações base Django |
| `core/settings/development.py` | Config desenvolvimento |
| `core/settings/production.py` | Config produção (Vercel) |
| `.env` | Variáveis de ambiente |
| `supabase/functions/process-ocr/` | Edge Function de OCR |

---

## Instruções para IA

1. **Segurança:** Nunca exponha secrets ou chaves no código
2. **Testes:** Novas features devem ter testes correspondentes
3. **Docstrings:** Adicione documentação em código novo
4. **Commits:** Use Conventional Commits
5. **Dependências:** Adicione ao `requirements.txt` ou `package.json`
6. **Auditoria:** Novos models CRUD são automaticamente auditados

---

## Variáveis de Ambiente Essenciais

```bash
SECRET_KEY              # Chave Django
DEBUG                   # True/False
POSTGRES_URL            # PostgreSQL (Supabase)
DATABASE_MONGODB_LOGS   # MongoDB Atlas
SUPABASE_URL            # URL do Supabase
SUPABASE_SERVICE_ROLE_KEY  # Chave admin Supabase
GEMINI_API_KEY          # Chaves Gemini (múltiplas, separadas por vírgula)
BROWSERLESS_API_KEY     # Token do Browserless
```

---

## Documentação Relacionada

- [README.md](../README.md) - Visão geral do projeto
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Guia de contribuição
- [docs/OCR.md](OCR.md) - Sistema de OCR
- [docs/DOCKER.md](DOCKER.md) - Configuração Docker
- [docs/PROXIMOS_PASSOS.md](PROXIMOS_PASSOS.md) - Roadmap

---

**Última atualização:** 2024-12-28
