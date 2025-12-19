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

# Collect static files
echo "📁 Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput --clear

echo "=== ✅ Build concluído com sucesso! ==="
