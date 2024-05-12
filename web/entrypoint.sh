#!/bin/sh
python manage.py migrate
python manage.py collectstatic
python manage.py create_default_superuser
python manage.py create_default_notification_types
mkdir -p /django_static/static/
cp -r /app/collected_static/. /django_static/static/
daphne -b 0.0.0.0 -p 8000 main.asgi:application