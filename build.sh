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

# Populate legacy bidding (fix for existing materials)
echo "Populating legacy bidding..."
python3 manage.py populate_legacy_bidding

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
