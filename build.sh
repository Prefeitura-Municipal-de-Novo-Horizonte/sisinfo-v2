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

###############################################################
set -e
yum install -y yum-utils rpmdevtools
cd /tmp
yumdownloader --resolve \
    cairo.x86_64 \
    gdk-pixbuf2.x86_64 \
    libffi.x86_64 \
    pango.x86_64 \
    expat.x86_64 \
    libmount.x86_64 \
    libuuid.x86_64 \
    libblkid.x86_64 \
    glib2.x86_64 \

rpmdev-extract -- *rpm

mkdir /opt/lib
cp -P -r /tmp/*/usr/lib64/* /opt/lib
# pixbuf need list loaders cache
# https://developer.gnome.org/gdk-pixbuf/stable/gdk-pixbuf-query-loaders.html
PIXBUF_BIN=$(find /tmp -name gdk-pixbuf-query-loaders-64)
GDK_PIXBUF_MODULEDIR=$(find /opt/lib/gdk-pixbuf-2.0/ -name loaders)
export GDK_PIXBUF_MODULEDIR
$PIXBUF_BIN > /opt/lib/loaders.cache
# pixbuf need mime database
# https://www.linuxtopia.org/online_books/linux_desktop_guides/gnome_2.14_admin_guide/mimetypes-database.html
cp -r /usr/share/mime /opt/lib/mime

RUNTIME=$(echo "$AWS_EXECUTION_ENV" | cut -d _ -f 3)
export RUNTIME
mkdir -p "/opt/python/lib/$RUNTIME/site-packages"
python -m pip install "weasyprint<53.0" -t "/opt/python/lib/$RUNTIME/site-packages"

cd /opt
# zip -r /out/layer.zip lib/* python/*
###############################################################

echo 'Version python'
python3 --version
echo 'Version pango'
pango-view --version
echo "Versões PIP FREEZE..."
pip freeze