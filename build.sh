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

# Recuperação de dados (legacy) removida em Clean-up
# (Código de restore_material_reports_from_json e fix_orphan removidos)


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

# Corrigir laudos abertos com licitações fechadas (v1)
python3 manage.py check_procedure "close_stale_reports_v1" > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "Fechando laudos com licitações inativas..."
    python3 manage.py close_stale_reports --dry-run && \
    python3 manage.py close_stale_reports && \
    python3 manage.py mark_procedure "close_stale_reports_v1" --notes "Fechamento automático de laudos" || \
    python3 manage.py mark_procedure "close_stale_reports_v1" --failed --notes "Falha no fechamento de laudos"
else
    echo "Fechamento de laudos já executado (pulando...)"
fi

# Corrigir MaterialReports órfãos (v1)
python3 manage.py check_procedure "fix_orphan_material_reports_v1" > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "Corrigindo MaterialReports órfãos..."
    python3 manage.py fix_orphan_material_reports --dry-run && \
    python3 manage.py fix_orphan_material_reports && \
    python3 manage.py mark_procedure "fix_orphan_material_reports_v1" --notes "Correção de dados órfãos" || \
    python3 manage.py mark_procedure "fix_orphan_material_reports_v1" --failed --notes "Falha na correção"
else
    echo "Correção de dados órfãos já executada (pulando...)"
fi

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
