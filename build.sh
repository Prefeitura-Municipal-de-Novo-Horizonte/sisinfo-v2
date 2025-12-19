#!/bin/bash
set -e  # Exit on error

echo "=== SISInfo V2 - Build Script ==="
echo "Iniciando build para Vercel..."

# Create a virtual environment
echo "📦 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Garantir diretório de logs para o Django
mkdir -p logs

# Install dependencies with cache optimization
echo "📦 Instalando dependências..."
pip install --upgrade pip setuptools wheel -q
pip install -r requirements.txt -q

# Apply migrations
echo "🔄 Aplicando migrações..."
python3 manage.py migrate --noinput

# Verificar se precisa carregar dados iniciais (migração Supabase)
echo "=== VERIFICANDO DADOS INICIAIS ==="
python3 manage.py check_procedure "initial_data_load_v1" > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "📥 Carregando dados iniciais (migração para Supabase)..."
    if [ -f "core/fixtures/initial_data.json" ]; then
        # Desabilitar set -e temporariamente para capturar erro de loaddata
        set +e
        python3 manage.py loaddata core/fixtures/initial_data.json --verbosity 2
        LOADDATA_RESULT=$?
        set -e
        
        if [ $LOADDATA_RESULT -eq 0 ]; then
            python3 manage.py mark_procedure "initial_data_load_v1" --notes "Dados migrados do Aiven para Supabase"
            echo "✅ Dados carregados com sucesso!"
        else
            echo "⚠️  Falha no loaddata (código: $LOADDATA_RESULT)"
            echo "⚠️  Continuando sem dados iniciais - aplicação iniciará vazia"
            python3 manage.py mark_procedure "initial_data_load_v1" --failed --notes "Falha no carregamento - banco vazio"
        fi
    else
        echo "⚠️  Arquivo initial_data.json não encontrado, pulando..."
        python3 manage.py mark_procedure "initial_data_load_v1" --notes "Arquivo não encontrado - banco vazio"
    fi
else
    echo "✅ Dados iniciais já carregados (pulando...)"
fi

# Executar procedimentos de manutenção (apenas uma vez cada)
echo "=== PROCEDIMENTOS DE MANUTENÇÃO ==="

# Consolidar duplicatas (v1)
python3 manage.py check_procedure "consolidate_duplicates_v1" > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "🔧 Consolidando duplicatas..."
    python3 manage.py consolidate_duplicates --auto --threshold 0.98 && \
    python3 manage.py mark_procedure "consolidate_duplicates_v1" --notes "Consolidação automática" || \
    python3 manage.py mark_procedure "consolidate_duplicates_v1" --failed --notes "Falha"
else
    echo "✅ Consolidação já executada"
fi

# Limpar licitações duplicadas (v1)
python3 manage.py check_procedure "clean_duplicate_biddings_v1" > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "🔧 Limpando licitações duplicadas..."
    python3 manage.py clean_duplicate_biddings && \
    python3 manage.py mark_procedure "clean_duplicate_biddings_v1" --notes "Limpeza executada" || \
    python3 manage.py mark_procedure "clean_duplicate_biddings_v1" --failed --notes "Falha"
else
    echo "✅ Limpeza de licitações já executada"
fi

# Corrigir laudos com licitações fechadas (v1)
python3 manage.py check_procedure "close_stale_reports_v1" > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "🔧 Fechando laudos inativos..."
    python3 manage.py close_stale_reports && \
    python3 manage.py mark_procedure "close_stale_reports_v1" --notes "Fechamento automático" || \
    python3 manage.py mark_procedure "close_stale_reports_v1" --failed --notes "Falha"
else
    echo "✅ Fechamento de laudos já executado"
fi

# Corrigir MaterialReports órfãos (v1)
python3 manage.py check_procedure "fix_orphan_material_reports_v1" > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "🔧 Corrigindo dados órfãos..."
    python3 manage.py fix_orphan_material_reports && \
    python3 manage.py mark_procedure "fix_orphan_material_reports_v1" --notes "Correção executada" || \
    python3 manage.py mark_procedure "fix_orphan_material_reports_v1" --failed --notes "Falha"
else
    echo "✅ Correção de órfãos já executada"
fi

# Collect static files
echo "📁 Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput --clear

echo "=== ✅ Build concluído com sucesso! ==="
