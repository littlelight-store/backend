#!/usr/bin/env sh

echo "Starting celery worker"
cd /opt/app/src ; celery -A boosting worker -l info & celery -A boosting beat -l info
