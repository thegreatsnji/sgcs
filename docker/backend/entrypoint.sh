#!/bin/bash
set -e

echo "A aguardar PostgreSQL..."
while ! python -c "
import socket
import os
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
try:
    s.connect((os.environ.get('DB_HOST', 'db'), int(os.environ.get('DB_PORT', '5432'))))
    s.close()
    exit(0)
except OSError:
    exit(1)
"; do
  sleep 1
done

echo "PostgreSQL disponível."

python manage.py migrate --noinput
python manage.py seed_rbac

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

if [ "$APP_ENV" = "development" ]; then
  if [ "${SGCS_SEED_DEMO:-1}" != "0" ]; then
    python manage.py seed_demo --skip-if-present || true
  fi
  exec python manage.py runserver 0.0.0.0:8000
else
  python manage.py collectstatic --noinput
  WORKERS="${GUNICORN_WORKERS:-3}"
  exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "$WORKERS" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
fi
