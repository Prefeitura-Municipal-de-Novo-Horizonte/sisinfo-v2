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

# Executar comandos de recuperação apenas uma vez (usando banco de dados)
echo "=== VERIFICANDO PROCEDIMENTOS DE RECUPERAÇÃO ==="

# Recuperação de dados (v1)
python3 manage.py check_procedure "data_recovery_v1" > /dev/null 2>&1
if [ $? -eq 1 ]; then
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
    
    # Marcar como concluído no banco
    python3 manage.py mark_procedure "data_recovery_v1" --notes "Recuperação inicial de dados"
    echo "=== RECUPERAÇÃO CONCLUÍDA ==="
else
    echo "Recuperação de dados já foi executada anteriormente (pulando...)"
fi


# Executar procedimentos de manutenção (apenas uma vez cada)
echo "=== VERIFICANDO PROCEDIMENTOS DE MANUTENÇÃO ==="

# Consolidar duplicatas (v1)
python3 manage.py check_procedure "consolidate_duplicates_v1" > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "Consolidando fornecedores e materiais duplicados..."
    python3 manage.py consolidate_duplicates --auto --threshold 0.98 && \
    python3 manage.py mark_procedure "consolidate_duplicates_v1" --notes "Consolidação automática de duplicatas" || \
    python3 manage.py mark_procedure "consolidate_duplicates_v1" --failed --notes "Falha na consolidação"
else
    echo "Consolidação de duplicatas já executada (pulando...)"
fi

# Limpar licitações duplicadas (v1)
python3 manage.py check_procedure "clean_duplicate_biddings_v1" > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "Limpando licitações duplicadas..."
    python3 manage.py clean_duplicate_biddings && \
    python3 manage.py mark_procedure "clean_duplicate_biddings_v1" --notes "Limpeza de licitações duplicadas" || \
    python3 manage.py mark_procedure "clean_duplicate_biddings_v1" --failed --notes "Falha na limpeza"
else
    echo "Limpeza de licitações duplicadas já executada (pulando...)"
fi

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
