#!/bin/sh
python manage.py migrate
python manage.py collectstatic
python manage.py create_superuser -u root -p root
mkdir -p /django_static/static/
cp -r /app/collected_static/. /django_static/static/
gunicorn --bind 0.0.0.0:8000 main.wsgi