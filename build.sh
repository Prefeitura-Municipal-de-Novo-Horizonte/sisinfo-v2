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

# -----------------------------------------------------------
# PRODUCTION DATA FIXES & SYNC
# -----------------------------------------------------------
echo "🛠️ Executando correções de dados e sincronização..."
python3 manage.py fix_material_names
python3 manage.py update_supplier_cnpjs
python3 manage.py sync_bidding_materials
# -----------------------------------------------------------


# Criar superusuário se variáveis estiverem definidas
echo "=== VERIFICANDO SUPERUSUÁRIO ==="
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "📧 Criando/atualizando superusuário..."
    python3 manage.py shell << 'EOF'
from authenticate.models import ProfessionalUser
import os

email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
first_name = os.environ.get("DJANGO_SUPERUSER_FIRST_NAME", "Admin")
last_name = os.environ.get("DJANGO_SUPERUSER_LAST_NAME", "Sistema")

user, created = ProfessionalUser.objects.get_or_create(
    email=email,
    defaults={
        'first_name': first_name,
        'last_name': last_name,
        'is_tech': True,
        'is_admin': True,
        'is_active': True,
    }
)
if created:
    user.set_password(password)
    user.save()
    print(f"✅ Superusuário criado: {email}")
else:
    print(f"ℹ️  Superusuário já existe: {email}")
EOF
else
    echo "⚠️  DJANGO_SUPERUSER_EMAIL/PASSWORD não definidos, pulando..."
fi

# Collect static files
echo "📁 Coletando arquivos estáticos..."
python3 manage.py collectstatic --noinput --clear

echo "=== ✅ Build concluído com sucesso! ==="
