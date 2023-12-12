#!/bin/bash
# Create a virtual environment
# echo "Creating a virtual environment..."
# python3.9 -m venv venv
# echo "Acessing a virtual environment..."
# source venv/bin/activate
pwd
###############################################################
set -e
yum install -y yum-utils rpmdevtools
LOCAL_PATH=$(pwd)
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
    cairo-devel.x86_64 \

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
python3 -m pip install "weasyprint<52.0" -t "/opt/python/lib/$RUNTIME/site-packages"

cd $LOCAL_PATH
# cd /opt
# zip -r /out/layer.zip lib/* python/*
###############################################################

# Install the latest version of pip
echo "Installing the latest version of pip..."
python3 -m pip install --upgrade pip 
echo "Upgrading the latest version of setuptools and wheel ..."
python3 -m pip install --upgrade setuptools wheel

# Build the project
echo "Building the project..."
ls -la
pwd
python3 -m pip install -r requirements.txt

# Make migrations
echo "Making migrations..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear



echo 'Version python'
python3 --version
echo 'Version pango'
pango-view --version
echo "Versões PIP FREEZE..."
pip freeze
weasyprint --info