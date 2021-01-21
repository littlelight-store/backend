#!/usr/bin/env sh

echo "Waiting for database to init..."

echo "Run migrations"
python3 /opt/app/src/manage.py migrate --noinput

# collect static files
echo "Collect static"
python3 /opt/app/src/manage.py collectstatic --noinput

echo "Start server"
cd /opt/app/src || exit ; uvicorn boosting.asgi:application --reload --host 0.0.0.0 --port 8000
#python3 /opt/app/src/manage.py runserver 0.0.0.0:8000
