# Sistema de Auditoria - MongoDB

Documentação do sistema de auditoria que registra todas as operações no MongoDB.

**Última atualização:** 2024-12-27

---

## Visão Geral

O SISInfo V2 possui um sistema de auditoria completo que registra:
- Operações CRUD (Create, Read, Update, Delete)
- Autenticação (login, logout, troca de senha)
- Mudanças detalhadas (before/after)

Os logs são armazenados no **MongoDB Atlas** para alta performance e escalabilidade.

---

## Configuração

### Variável de Ambiente

```bash
# MongoDB Atlas (Produção)
DATABASE_MONGODB_LOGS=mongodb+srv://user:password@cluster.mongodb.net/sisinfo_audit

# MongoDB Local (Docker)
DATABASE_MONGODB_LOGS=mongodb://sisinfo:sisinfo@localhost:27017/sisinfo_audit?authSource=admin
```

### Docker Compose (Desenvolvimento)

```bash
docker-compose up -d mongodb
```

---

## Arquitetura

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Django    │────▶│  AuditService   │────▶│   MongoDB    │
│   Signals   │     │   (services.py) │     │   Atlas      │
└─────────────┘     └─────────────────┘     └──────────────┘
```

### Componentes

| Arquivo | Descrição |
|---------|-----------|
| `audit/services.py` | `AuditService.log_event()` - registro de logs |
| `audit/signals.py` | Signals automáticos para CRUD |
| `audit/middleware.py` | Captura requisições para contexto |
| `audit/mongodb.py` | Conexão com MongoDB |

---

## Uso

### Registro Automático

Todos os modelos listados em `AUDITED_MODELS` são auditados automaticamente:

```python
# audit/signals.py
AUDITED_MODELS = [
    'ProfessionalUser',
    'Bidding',
    'Supplier',
    'MaterialBidding',
    'Invoice',
    'DeliveryNote',
    # ...
]
```

### Registro Manual

```python
from audit.services import AuditService

# Registrar evento customizado
AuditService.log_event(
    event_type='crud',
    user=request.user,
    model_name='Invoice',
    object_id=invoice.id,
    action='approve',
    changes={'status': {'before': 'pending', 'after': 'approved'}},
    request=request,
    metadata={'reason': 'Aprovado pelo fiscal'}
)
```

---

## Estrutura do Log

```json
{
  "event_type": "crud",
  "action": "update",
  "timestamp": "2024-12-27T15:30:00Z",
  "user_id": 1,
  "username": null,
  "email": "usuario@email.com",
  "model": "Invoice",
  "object_id": "123",
  "changes": {
    "status": {
      "before": "pending",
      "after": "completed"
    }
  },
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "path": "/fiscal/invoices/123/",
  "method": "POST",
  "metadata": {}
}
```

---

## Comandos de Manutenção

### Backup de Logs

```bash
# Backup completo
python manage.py backup_audit_logs

# Backup dos últimos 30 dias
python manage.py backup_audit_logs --days 30

# Backup comprimido
python manage.py backup_audit_logs --days 30 --compress

# Filtrar por modelo
python manage.py backup_audit_logs --model Invoice
```

### Limpeza de Logs

```bash
# Ver o que seria deletado (dry-run)
python manage.py clean_audit_logs --days 90 --dry-run

# Deletar logs antigos (> 90 dias)
python manage.py clean_audit_logs --days 90

# Backup antes de limpar
python manage.py clean_audit_logs --days 90 --backup-first
```

---

## Índices MongoDB

Para melhor performance, crie os índices:

```javascript
use sisinfo_audit

db.audit_logs.createIndex({ "timestamp": -1 })
db.audit_logs.createIndex({ "user_id": 1, "timestamp": -1 })
db.audit_logs.createIndex({ "model": 1, "timestamp": -1 })
db.audit_logs.createIndex({ "event_type": 1, "action": 1 })
db.audit_logs.createIndex({ "object_id": 1, "model": 1 })
```

---

## Adicionar Novo Modelo à Auditoria

1. Adicione o nome do modelo em `audit/signals.py`:

```python
AUDITED_MODELS = [
    # ...existentes
    'SeuNovoModelo',  # Adicione aqui
]
```

2. O modelo será auditado automaticamente via signals.

---

## Consultas Úteis (MongoDB)

### Logs de um usuário específico
```javascript
db.audit_logs.find({ "user_id": 1 }).sort({ "timestamp": -1 })
```

### Todas as deleções
```javascript
db.audit_logs.find({ "action": "delete" }).sort({ "timestamp": -1 })
```

### Alterações em um objeto específico
```javascript
db.audit_logs.find({ 
  "model": "Invoice", 
  "object_id": "123" 
}).sort({ "timestamp": -1 })
```

### Logins do último dia
```javascript
db.audit_logs.find({ 
  "event_type": "auth",
  "action": "login",
  "timestamp": { $gte: new Date(Date.now() - 24*60*60*1000) }
})
```

---

## Troubleshooting

### Logs não estão sendo registrados

1. Verificar conexão MongoDB: `DATABASE_MONGODB_LOGS`
2. Verificar se modelo está em `AUDITED_MODELS`
3. Verificar logs do Django para erros de conexão

### Conexão lenta

1. Verificar região do MongoDB Atlas
2. Adicionar índices necessários
3. Considerar aumentar timeout de conexão

---

## Referências

- [MongoDB Atlas](https://www.mongodb.com/docs/atlas/)
- [pymongo Documentation](https://pymongo.readthedocs.io/)
- [docs/DOCKER.md](DOCKER.md) - MongoDB local
