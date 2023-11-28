#!/bin/bash

# Create a virtual environment
echo "Creating a virtual environment..."
python3.9 -m venv .venv
source .venv/bin/activate

# Install the latest version of pip
echo "Installing the latest version of pip..."
python -m pip install --upgrade pip

# Build the project
echo "Building the project..."
python -m pip install -r requirements.txt

# Make migrations
echo "Making migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Install Vercel Analycts
npm i @vercel/analytics
npm install

# Carrega Keynotes
#python manage.py loaddata category.json
#python manage.py loaddata products.json