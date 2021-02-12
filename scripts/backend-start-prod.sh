#!/usr/bin/env sh

echo "Run migrations"
python3 /opt/app/src/manage.py migrate --noinput

# collect static files
# echo "Collect static"
python3 /opt/app/src/manage.py collectstatic --noinput

echo "Starting production server"
cd /opt/app/src || exit ; uvicorn boosting.asgi:application --host 0.0.0.0 --port 8000
