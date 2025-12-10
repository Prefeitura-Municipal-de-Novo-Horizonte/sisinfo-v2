# Scripts de Backup - Comparação

## 📋 Resumo Rápido

**Use `backup.sh`** - É o script novo e completo!

## 🆚 Diferenças

### `backup.sh` (NOVO) ✅ RECOMENDADO

**Criado em:** Dezembro 2024  
**Funcionalidades:**
- ✅ Backup de múltiplos ambientes (dev/produção/current)
- ✅ Formatos JSON e SQL
- ✅ Suporte a Docker automático
- ✅ Backup de bancos remotos via Docker
- ✅ Limpeza automática (mantém 10 backups)
- ✅ Interface colorida e amigável

**Como usar:**
```bash
./scripts/backup.sh                # Banco atual
./scripts/backup.sh dev            # Dev
./scripts/backup.sh production     # Produção
./scripts/backup.sh both           # Dev + Produção
```

---

### `backup_database.sh` (ANTIGO) 📖

**Criado em:** Novembro 2024  
**Funcionalidades:**
- ✅ Backup apenas em JSON
- ✅ Exclui auth.permission, contenttypes, sessions
- ✅ Limpeza automática (mantém 10 backups)
- ❌ Não suporta múltiplos ambientes
- ❌ Não suporta SQL
- ❌ Não usa Docker

**Como usar:**
```bash
./scripts/backup_database.sh       # Apenas banco atual
```

---

## 🎯 Qual Usar?

### Use `backup.sh` se:
- ✅ Quer fazer backup da produção sem editar .env
- ✅ Quer backup em SQL
- ✅ Quer usar Docker
- ✅ Quer a solução mais completa

### Use `backup_database.sh` se:
- ⚠️ Precisa do formato antigo exato
- ⚠️ Quer excluir auth.permission automaticamente
- ⚠️ Tem scripts que dependem dele

---

## 💡 Recomendação

**Migre para `backup.sh`!** 

O script antigo (`backup_database.sh`) pode ser mantido para compatibilidade, mas o novo é muito mais poderoso.

Se você tem scripts ou processos que usam `backup_database.sh`, considere migrar para:

```bash
# Antes
./scripts/backup_database.sh

# Depois
./scripts/backup.sh current --format json
```
