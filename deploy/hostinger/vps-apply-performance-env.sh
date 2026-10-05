#!/usr/bin/env bash
# SGCS — aplica variáveis de desempenho em .env.production (VPS).
#   cd /opt/sgcs && bash deploy/hostinger/vps-apply-performance-env.sh
set -euo pipefail

SGCS_DIR="${SGCS_DIR:-/opt/sgcs}"
cd "$SGCS_DIR"

ENV_FILE=".env.production"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: $SGCS_DIR/$ENV_FILE not found."
  exit 1
fi

set_kv() {
  local key="$1" val="$2"
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i "s|^${key}=.*|${key}=${val}|" "$ENV_FILE"
  else
    echo "${key}=${val}" >> "$ENV_FILE"
  fi
}

cp -a "$ENV_FILE" "${ENV_FILE}.bak.$(date +%Y%m%d%H%M%S)"

set_kv REDIS_CACHE_URL "redis://redis:6379/1"
set_kv CELERY_RESULT_BACKEND "redis://redis:6379/2"
set_kv DB_CONN_MAX_AGE "120"
set_kv CACHE_TIMEOUT "300"
set_kv GUNICORN_WORKERS "3"
set_kv CELERY_CONCURRENCY "2"
set_kv CELERY_PREFETCH "1"

chmod 600 "$ENV_FILE"

if [[ -f deploy/nginx/generated/default-ssl.conf ]] \
  && ! grep -q 'sgcs-performance.conf' deploy/nginx/generated/default-ssl.conf; then
  sed -i '/client_max_body_size/a\    include /etc/nginx/snippets/sgcs-performance.conf;' \
    deploy/nginx/generated/default-ssl.conf
  echo "Added nginx performance include to default-ssl.conf"
fi

echo "==> Updated $ENV_FILE (backup created)."
grep -E '^(REDIS_CACHE_URL|CELERY_RESULT_BACKEND|DB_CONN_MAX_AGE|GUNICORN_WORKERS)=' "$ENV_FILE"

if [[ -x deploy/hostinger/compose-prod.sh ]] || [[ -f deploy/hostinger/compose-prod.sh ]]; then
  echo "==> Rebuilding containers..."
  bash deploy/hostinger/compose-prod.sh up -d --build
else
  echo "Run: docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build"
fi

echo "Done."
