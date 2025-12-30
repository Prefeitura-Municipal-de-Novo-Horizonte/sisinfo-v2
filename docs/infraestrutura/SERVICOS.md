# Serviços Externos - SISInfo V2

Guia de todos os serviços externos utilizados pelo sistema.

**Última atualização:** 2025-12-29

---

## 📋 Visão Geral

| Serviço | Uso | Plano |
|---------|-----|-------|
| Vercel | Deploy e hosting | Free |
| Supabase | PostgreSQL + Storage | Free |
| Upstash | Redis (Cache) | Free |
| Sentry | Error tracking | Free (5k erros/mês) |
| MongoDB Atlas | Auditoria | Free |
| Browserless.io | Geração de PDFs | Free (1k PDFs/mês) |

---

## 🔗 Links dos Dashboards

| Serviço | URL |
|---------|-----|
| **Vercel** | https://vercel.com/dashboard |
| **Supabase** | https://supabase.com/dashboard |
| **Upstash** | https://console.upstash.com |
| **Sentry** | https://sentry.io |
| **MongoDB Atlas** | https://cloud.mongodb.com |
| **Browserless** | https://browserless.io/dashboard |

---

## ⚙️ Variáveis de Ambiente

### Vercel (Produção)

```bash
# Django
SECRET_KEY=***
ALLOWED_HOSTS=***.vercel.app
DJANGO_SETTINGS_MODULE=core.settings.production

# Supabase
POSTGRES_URL=***
POSTGRES_URL_NON_POOLING=***
SUPABASE_URL=***
SUPABASE_ANON_KEY=***
SUPABASE_SERVICE_ROLE_KEY=***

# Upstash Redis
UPSTASH_REDIS_REST_URL=***
UPSTASH_REDIS_REST_TOKEN=***
# (Opcional) Redis Local
# REDIS_URL=redis://localhost:6379/0

# Upstash QStash (Se utilizado)
QSTASH_URL=***
QSTASH_TOKEN=***
QSTASH_CURRENT_SIGNING_KEY=***
QSTASH_NEXT_SIGNING_KEY=***

# MongoDB
DATABASE_MONGODB_LOGS=***

# Sentry
SENTRY_DSN=***

# Gemini (OCR)
GEMINI_API_KEY=***

# Browserless
BROWSERLESS_API_KEY=***

# Email
EMAIL_BACKEND=***
EMAIL_HOST=***
EMAIL_PORT=***
EMAIL_USE_TLS=***
EMAIL_HOST_USER=***
EMAIL_HOST_PASSWORD=***

# Logging
LOG_LEVEL=INFO
```

---

## 🛠️ Desenvolvimento Local

### Serviços Docker

```bash
# Iniciar todos
docker-compose up -d

# Status
docker-compose ps
```

| Container | Porta | Uso |
|-----------|-------|-----|
| sisinfo_redis | 6379 | Cache |
| sisinfo_mongo | 27017 | Auditoria |
| sisinfo_browserless | 3000 | PDFs |

### Supabase Local

```bash
# Iniciar
npx supabase start

# Parar
npx supabase stop
```

---

## 📊 Limites Free Tier

| Serviço | Limite | Uso Estimado |
|---------|--------|--------------|
| Vercel | 100GB bandwidth | Baixo |
| Supabase | 500MB DB | ~50MB |
| Upstash Redis | 10k comandos/dia | Baixo |
| Upstash QStash | 500 mensagens/dia | Baixo |
| Sentry | 5k erros/mês | Baixo |
| MongoDB Atlas | 512MB | ~10MB |
| Browserless | 1k PDFs/mês | Médio |

---

## 🔐 Onde estão as credenciais?

- **Produção:** Vercel Dashboard → Settings → Environment Variables
- **Desenvolvimento:** Arquivo `.env` (não commitado)

> ⚠️ **NUNCA** commite credenciais no repositório!
