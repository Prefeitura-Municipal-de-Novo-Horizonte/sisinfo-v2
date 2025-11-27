#!/bin/bash

# Script de backup automático do banco de dados
# Executar antes de cada deploy

# Configurações
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="${DB_NAME:-sisinfo}"
BACKUP_FILE="${BACKUP_DIR}/backup_${DB_NAME}_${DATE}.json"

# Criar diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

echo "========================================="
echo "Backup do Banco de Dados - SISInfo V2"
echo "========================================="
echo "Data: $(date)"
echo "Arquivo: $BACKUP_FILE"
echo ""

# Fazer backup completo em JSON
echo "Exportando dados..."
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --indent 2 \
    --exclude auth.permission \
    --exclude contenttypes \
    --exclude sessions \
    > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup criado com sucesso!"
    echo "Tamanho: $(du -h "$BACKUP_FILE" | cut -f1)"
    
    # Manter apenas os últimos 10 backups
    echo ""
    echo "Limpando backups antigos (mantendo últimos 10)..."
    ls -t "$BACKUP_DIR"/backup_*.json | tail -n +11 | xargs -r rm
    
    echo ""
    echo "Backups disponíveis:"
    ls -lh "$BACKUP_DIR"/backup_*.json | tail -5
else
    echo "❌ Erro ao criar backup!"
    exit 1
fi

echo ""
echo "========================================="
echo "Backup concluído!"
echo "========================================="
