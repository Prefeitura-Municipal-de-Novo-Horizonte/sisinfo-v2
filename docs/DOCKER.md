# Docker Compose - SISInfo V2

Este arquivo configura os serviços necessários para desenvolvimento local.

## Serviços

### PostgreSQL
- **Imagem**: postgres:latest
- **Container**: sisinfo_postgres
- **Porta**: 5432
- **Credenciais**:
  - Usuário: `sisinfo`
  - Senha: `sisinfo`
  - Database: `sisinfo`
- **Volume**: `postgres_data` (persistente)

### MongoDB
- **Imagem**: mongo:7.0
- **Container**: sisinfo_mongodb
- **Porta**: 27017
- **Credenciais**:
  - Usuário: `sisinfo`
  - Senha: `sisinfo`
  - Database: `sisinfo_audit`
- **Volumes**: 
  - `mongodb_data` (dados)
  - `mongodb_config` (configuração)

### Browserless
- **Imagem**: browserless/chrome:latest
- **Container**: sisinfo_browserless
- **Porta**: 3000
- **Token**: `sisinfo_dev_token`
- **Uso**: Geração de PDFs de laudos técnicos
- **Configurações**:
  - Max sessões concorrentes: 10
  - Timeout de conexão: 60s
  - Tamanho máximo da fila: 10

## Comandos

### Iniciar serviços
```bash
docker-compose up -d
```

### Ver logs
```bash
# PostgreSQL
docker-compose logs -f db

# MongoDB
docker-compose logs -f mongodb
```

### Parar serviços
```bash
docker-compose down
```

### Parar e remover volumes (⚠️ APAGA DADOS)
```bash
docker-compose down -v
```

## Configuração no .env

Para usar o MongoDB local, configure no `.env`:

```bash
# MongoDB Local (Docker)
DATABASE_MONGODB_LOGS=mongodb://sisinfo:sisinfo@localhost:27017/sisinfo_audit?authSource=admin
```

Para produção (MongoDB Atlas):
```bash
# MongoDB Atlas (Produção)
DATABASE_MONGODB_LOGS=mongodb+srv://user:password@cluster.mongodb.net/sisinfo_audit
```

### Browserless

Para usar o Browserless local, configure no `.env`:

```bash
# Browserless Local (Docker)
BROWSERLESS_API_KEY=ws://localhost:3000?token=sisinfo_dev_token
```

Para produção (Browserless.io):
```bash
# Browserless.io (Produção)
BROWSERLESS_API_KEY=your_browserless_io_api_key
```

## Acessar MongoDB

### Via Docker
```bash
docker exec -it sisinfo_mongodb mongosh -u sisinfo -p sisinfo --authenticationDatabase admin
```

### Via MongoDB Compass
- Connection String: `mongodb://sisinfo:sisinfo@localhost:27017/?authSource=admin`

## Criar Índices

Após iniciar o MongoDB, crie os índices recomendados:

```javascript
use sisinfo_audit

db.audit_logs.createIndex({ "timestamp": -1 })
db.audit_logs.createIndex({ "user_id": 1, "timestamp": -1 })
db.audit_logs.createIndex({ "model": 1, "timestamp": -1 })
db.audit_logs.createIndex({ "event_type": 1, "action": 1 })
db.audit_logs.createIndex({ "object_id": 1, "model": 1 })
```

## Troubleshooting

### Porta já em uso
Se a porta 27017 já estiver em uso, altere no `docker-compose.yaml`:
```yaml
ports:
  - "27018:27017"  # Mapeia porta 27018 do host para 27017 do container
```

E atualize o `.env`:
```bash
DATABASE_MONGODB_LOGS=mongodb://sisinfo:sisinfo@localhost:27018/sisinfo_audit?authSource=admin
```

### Resetar MongoDB
```bash
docker-compose down
docker volume rm sisinfo-v2_mongodb_data sisinfo-v2_mongodb_config
docker-compose up -d mongodb
```
