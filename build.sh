#!/bin/bash

# Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv venv
echo "Acessing a virtual environment..."
source venv/bin/activate

# Garantir diretório de logs para o Django
echo "Garantindo diretório logs para logging..."
mkdir -p logs

# Install the latest version of pip
echo "Installing the latest version of pip..."
python3 -m pip install --upgrade pip 
echo "Upgrading the latest version of setuptools and wheel ..."
python3 -m pip install --upgrade setuptools wheel

# Build the project
echo "Building the project..."
python3 -m pip install -r requirements.txt

# Apply migrations (migrations should be created locally, not in build)
echo "Applying migrations..."
python3 manage.py migrate --noinput

# Executar comandos de recuperação apenas uma vez (usando arquivo de flag)
RECOVERY_FLAG=".recovery_completed"

if [ ! -f "$RECOVERY_FLAG" ]; then
    echo "=== EXECUTANDO RECUPERAÇÃO DE DADOS (PRIMEIRA VEZ) ==="
    
    # Restaurar MaterialReports do backup (se existir)
    if [ -f "backup/backup_24112025.json" ]; then
        echo "Restaurando MaterialReports do backup..."
        python3 manage.py restore_material_reports_from_json backup/backup_24112025.json --force || true
    fi
    
    # Corrigir MaterialReports órfãos (fallback)
    echo "Corrigindo MaterialReports órfãos..."
    python3 manage.py fix_orphan_material_reports || true
    
    # Populate legacy bidding (fix for existing materials)
    echo "Populating legacy bidding..."
    python3 manage.py populate_legacy_bidding || true
    
    # Marcar como concluído
    touch "$RECOVERY_FLAG"
    echo "=== RECUPERAÇÃO CONCLUÍDA ==="
else
    echo "Recuperação já foi executada anteriormente (pulando...)"
fi

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
