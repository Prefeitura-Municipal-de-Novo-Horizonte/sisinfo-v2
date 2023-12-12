#!/bin/bash
# Create a virtual environment
echo "Creating a virtual environment..."
python3.9 -m venv venv
echo "Acessing a virtual environment..."
source venv/bin/activate

# Install the latest version of pip
echo "Installing the latest version of pip..."
python -m pip install --upgrade pip
echo "Upgrading the latest version of setuptools and wheel ..."
python -m pip install --upgrade setuptools wheel

# Build the project
echo "Building the project..."
python -m pip install -r requirements.txt --no-cache-dir

# Make migrations
echo "Making migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

./layer_builder.sh

echo 'Version python'
python3 --version
echo 'Version pango'
pango-view --version
echo "Versões PIP FREEZE..."
pip freeze