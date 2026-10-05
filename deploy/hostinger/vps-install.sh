#!/usr/bin/env bash
# SGCS — instalação inicial no VPS Hostinger (Ubuntu 22.04+).
# Executar como root no servidor:
#   curl -fsSL ... | bash
# ou, com o repo já clonado:
#   bash deploy/hostinger/vps-install.sh
set -euo pipefail

SGCS_DIR="${SGCS_DIR:-/opt/sgcs}"
REPO_URL="${REPO_URL:-https://github.com/thegreatsnji/sgcs.git}"
BRANCH="${BRANCH:-main}"
VPS_IP="${VPS_IP:-148.230.113.108}"
VPS_HOST="${VPS_HOST:-srv1946391.hstgr.cloud}"
STAFF_PASSWORD="${STAFF_PASSWORD:-Demo@2026!}"

echo "==> SGCS VPS install (dir: $SGCS_DIR)"

if ! command -v docker >/dev/null 2>&1; then
  echo "==> Installing Docker..."
  apt-get update -qq
  apt-get install -y ca-certificates curl git
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose plugin missing — update Docker or install compose-plugin."
  exit 1
fi

if [[ ! -d "$SGCS_DIR/.git" ]]; then
  echo "==> Cloning repository..."
  mkdir -p "$(dirname "$SGCS_DIR")"
  git clone --branch "$BRANCH" --depth 1 "$REPO_URL" "$SGCS_DIR"
else
  echo "==> Updating repository..."
  git -C "$SGCS_DIR" fetch --depth 1 origin "$BRANCH"
  git -C "$SGCS_DIR" checkout "$BRANCH"
  git -C "$SGCS_DIR" pull --ff-only origin "$BRANCH" || true
fi

cd "$SGCS_DIR"

if [[ ! -f .env.production ]]; then
  echo "==> Creating .env.production..."
  SECRET_KEY="$(docker run --rm python:3.13-slim python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || openssl rand -base64 48)"
  DB_PASSWORD="$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)"

  cat > .env.production <<EOF
APP_NAME=SGCS
APP_ENV=production
APP_DEBUG=false
SECRET_KEY=${SECRET_KEY}
ALLOWED_HOSTS=${VPS_IP},${VPS_HOST},localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://${VPS_IP},http://${VPS_HOST}
CSRF_TRUSTED_ORIGINS=http://${VPS_IP},http://${VPS_HOST}
VITE_API_URL=
DB_NAME=sgcs
DB_USER=sgcs
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
USE_REDIS=true
INSECURE_HTTP_PILOT=true
SECURE_SSL_REDIRECT=false
ALLOW_PUBLIC_REGISTRATION=false
ENABLE_API_DOCS=false
DJANGO_ADMIN_PATH=sgcs-admin
LOG_TO_FILES=true
LOG_JSON=true
LOG_LEVEL=INFO
SGCS_SEED_DEMO=0
HTTP_PORT=80
GUNICORN_WORKERS=2
EOF
  chmod 600 .env.production
  echo "    Saved .env.production (keep backup of DB_PASSWORD)."
else
  echo "==> .env.production already exists — keeping it."
fi

mkdir -p backend/data/private
if [[ ! -f backend/data/private/sauvida_staff.csv ]]; then
  cp backend/data/clinic/sauvida_staff.csv backend/data/private/sauvida_staff.csv
fi
printf '%s\n' "$STAFF_PASSWORD" > backend/data/private/pilot_initial_password.txt
chmod 600 backend/data/private/pilot_initial_password.txt

echo "==> Building and starting containers (may take several minutes)..."
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

echo "==> Waiting for backend..."
for i in $(seq 1 60); do
  if docker compose -f docker-compose.prod.yml exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ready/')" 2>/dev/null; then
    break
  fi
  sleep 5
done

echo "==> Staff users (skip if already imported)..."
docker compose -f docker-compose.prod.yml exec -T backend python manage.py seed_sauvida_staff \
  --file /app/data/private/sauvida_staff.csv \
  --password-file /app/data/private/pilot_initial_password.txt \
  --deactivate-demo-users \
  || docker compose -f docker-compose.prod.yml exec -T backend python manage.py seed_sauvida_staff \
  --file /app/data/private/sauvida_staff.csv \
  --update-existing \
  --password-file /app/data/private/pilot_initial_password.txt

echo ""
echo "=============================================="
echo " SGCS is running."
echo " Open: http://${VPS_IP}/"
echo " Login example: bacar.sanha@sauvida.gw"
echo " Password: (STAFF_PASSWORD / Demo@2026! by default)"
echo ""
echo " Later: point a domain + HTTPS, set INSECURE_HTTP_PILOT=false"
echo "       and update CORS/CSRF to https:// in .env.production"
echo "=============================================="
