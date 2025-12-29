# Docker Compose - SISInfo V2

Configuração dos serviços para desenvolvimento local.

**Última atualização:** 2025-12-29

---

## 📦 Serviços

| Serviço | Imagem | Container | Porta | Uso |
|---------|--------|-----------|-------|-----|
| Redis | redis:7-alpine | sisinfo_redis | 6379 | Cache, rate limiting, sessions |
| MongoDB | mongo:7.0-jammy | sisinfo_mongodb | 27017 | Logs de auditoria |
| Browserless | browserless/chrome | sisinfo_browserless | 3000 | Geração de PDFs |

> **Nota:** PostgreSQL é provido pelo Supabase local (`npx supabase start`).

---

## 🚀 Comandos de Desenvolvimento

### Ordem de Inicialização

```bash
# 1. Iniciar Supabase (PostgreSQL + Storage)
npx supabase start

# 2. Iniciar Docker Compose (Redis, MongoDB, Browserless)
docker-compose up -d

# 3. Instalar dependências Python
pip install -r requirements.txt -r requirements-dev.txt

# 4. Iniciar QStash local para background jobs
npx @upstash/qstash-cli dev

# 5. Aplicar migrações
python manage.py migrate

# 6. Iniciar servidor Django
python manage.py runserver
```

### Verificar Status

```bash
# Status dos containers
docker-compose ps

# Verificar Redis
docker exec sisinfo_redis redis-cli ping  # Deve retornar PONG

# Verificar MongoDB
docker exec sisinfo_mongodb mongosh --eval "db.adminCommand('ping')"

# Verificar Browserless
curl http://localhost:3000/
```

### Parar Serviços

```bash
# Parar Docker Compose
docker-compose down

# Parar Supabase
npx supabase stop
```

### Limpar Dados (⚠️ APAGA DADOS)

```bash
docker-compose down -v  # Remove volumes
```

---

## ⚙️ Variáveis de Ambiente (.env)

```bash
# === SUPABASE LOCAL ===
# Gerado automaticamente por 'npx supabase start'
POSTGRES_URL_NON_POOLING=postgresql://postgres:postgres@localhost:54322/postgres

# === DOCKER COMPOSE ===
# MongoDB
DATABASE_MONGODB_LOGS=mongodb://sisinfo:sisinfo@localhost:27017/sisinfo_audit?authSource=admin

# Redis
REDIS_URL=redis://localhost:6379/0
USE_REDIS=True

# Browserless
BROWSERLESS_API_KEY=ws://localhost:3000?token=sisinfo_dev_token

# === SENTRY (Opcional) ===
# Criar conta em https://sentry.io/signup/ (free tier)
SENTRY_DSN=
```

---

## 📝 Detalhes dos Serviços

### Redis

Usado para cache, rate limiting e sessões.

```bash
# Acessar CLI
docker exec -it sisinfo_redis redis-cli

# Comandos úteis
> KEYS *           # Listar todas as chaves
> FLUSHALL         # Limpar tudo (⚠️ cuidado)
> INFO             # Status do servidor
```

### MongoDB

Usado para logs de auditoria (app `audit`).

```bash
# Acessar shell
docker exec -it sisinfo_mongodb mongosh -u sisinfo -p sisinfo --authenticationDatabase admin

# Comandos úteis
> use sisinfo_audit
> db.audit_logs.countDocuments()
> db.audit_logs.find().limit(5).sort({timestamp: -1})
```

**Índices recomendados:**

```javascript
use sisinfo_audit
db.audit_logs.createIndex({ "timestamp": -1 })
db.audit_logs.createIndex({ "user_id": 1, "timestamp": -1 })
db.audit_logs.createIndex({ "model": 1, "timestamp": -1 })
```

### Browserless

Renderização de PDFs com Chrome headless.

- **Dashboard:** http://localhost:3000/
- **Token:** `sisinfo_dev_token`

---

## 🔧 Troubleshooting

### Porta já em uso

```bash
# Verificar quem está usando a porta
lsof -i :6379  # Redis
lsof -i :27017 # MongoDB
lsof -i :3000  # Browserless
```

### Resetar um container

```bash
docker-compose down
docker volume rm sisinfo-v2_redis_data       # Redis
docker volume rm sisinfo-v2_mongodb_data     # MongoDB
docker-compose up -d
```

### Redis não conecta

Verifique se `USE_REDIS=True` está no `.env`:

```bash
# O Django usa fallback para memória se USE_REDIS=False
USE_REDIS=True
```

---

## 🌐 Produção vs Desenvolvimento

| Serviço | Desenvolvimento | Produção |
|---------|-----------------|----------|
| PostgreSQL | Supabase local (`npx supabase start`) | Supabase Cloud |
| Redis | Docker (`redis:7-alpine`) | Upstash Redis |
| MongoDB | Docker (`mongo:7.0-jammy`) | MongoDB Atlas |
| Browserless | Docker (`browserless/chrome`) | Browserless.io |
| QStash | CLI (`npx @upstash/qstash-cli dev`) | Upstash QStash |
| Sentry | Opcional (mesmo DSN) | Sentry Cloud |

---

**Responsável:** Diretoria de TI  
**Contato:** ti@novohorizonte.sp.gov.br
