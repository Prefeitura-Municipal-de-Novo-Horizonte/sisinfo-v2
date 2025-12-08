#!/bin/bash
# Script para backup automático do banco de dados
# Uso: ./scripts/backup.sh [dev|production|both]

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Diretório de backups
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Função para exibir uso
usage() {
    echo "Uso: $0 [dev|production|both|current]"
    echo ""
    echo "Opções:"
    echo "  dev        - Backup do banco de desenvolvimento (localhost)"
    echo "  production - Backup do banco de produção (Aiven)"
    echo "  both       - Backup de ambos os bancos"
    echo "  current    - Backup do banco atualmente configurado (padrão)"
    echo ""
    echo "Exemplos:"
    echo "  $0              # Backup do banco atual"
    echo "  $0 production   # Backup apenas da produção"
    echo "  $0 both         # Backup de dev e produção"
    exit 1
}

# Função para criar backup
create_backup() {
    local env=$1
    
    echo -e "${GREEN}🔄 Criando backup do ambiente: ${env}${NC}"
    
    python manage.py backup_database \
        --environment "$env" \
        --format both \
        --output-dir "$BACKUP_DIR" \
        --prefix "backup"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backup de ${env} concluído!${NC}"
    else
        echo -e "${RED}❌ Erro ao criar backup de ${env}${NC}"
        exit 1
    fi
}

# Criar diretório de backups se não existir
mkdir -p "$BACKUP_DIR"

# Processar argumentos
ENV=${1:-current}

case $ENV in
    dev)
        create_backup "dev"
        ;;
    production)
        create_backup "production"
        ;;
    both)
        create_backup "dev"
        echo ""
        create_backup "production"
        ;;
    current)
        create_backup "current"
        ;;
    *)
        echo -e "${RED}❌ Ambiente inválido: $ENV${NC}"
        usage
        ;;
esac

# Listar backups criados
echo ""
echo -e "${YELLOW}📁 Backups disponíveis:${NC}"
ls -lh "$BACKUP_DIR" | tail -n +2 | awk '{print "  " $9 " (" $5 ")"}'

# Limpar backups antigos (manter últimos 10)
echo ""
echo -e "${YELLOW}🧹 Limpando backups antigos...${NC}"
cd "$BACKUP_DIR"
ls -t backup_*.json 2>/dev/null | tail -n +11 | xargs -r rm
ls -t backup_*.sql 2>/dev/null | tail -n +11 | xargs -r rm
cd ..

echo -e "${GREEN}✅ Processo de backup concluído!${NC}"
