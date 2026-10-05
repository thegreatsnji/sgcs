#!/usr/bin/env bash
# SGCS — activar HTTPS (Let's Encrypt) quando o domínio aponta para este VPS.
#
#   export DOMAIN=clinicasauvida.gw
#   export CERTBOT_EMAIL=admin@clinicasauvida.gw
#   bash deploy/hostinger/vps-enable-https.sh
#
# Requer: portas 80 e 443 abertas no firewall Hostinger.
set -euo pipefail

SGCS_DIR="${SGCS_DIR:-/opt/sgcs}"
DOMAIN="${DOMAIN:?Set DOMAIN=your.domain.gw}"
CERTBOT_EMAIL="${CERTBOT_EMAIL:?Set CERTBOT_EMAIL=for Let's Encrypt notices}"
VPS_IP="${VPS_IP:-}"

cd "$SGCS_DIR"
COMPOSE=(bash deploy/hostinger/compose-prod.sh)

if [[ ! -f .env.production ]]; then
  echo "ERROR: .env.production missing"
  exit 1
fi

if ! command -v certbot >/dev/null 2>&1; then
  echo "==> Installing certbot..."
  apt-get update -qq
  apt-get install -y certbot
fi

mkdir -p deploy/nginx/certs deploy/nginx/generated
chmod 700 deploy/nginx/certs

echo "==> Stopping web container (free port 80 for certbot standalone)..."
"${COMPOSE[@]}" stop web

echo "==> Obtaining certificate for $DOMAIN..."
certbot certonly --standalone --non-interactive --agree-tos \
  -m "$CERTBOT_EMAIL" \
  -d "$DOMAIN" \
  ${VPS_IP:+ -d "$VPS_IP"}

CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
install -m 644 "$CERT_DIR/fullchain.pem" deploy/nginx/certs/fullchain.pem
install -m 600 "$CERT_DIR/privkey.pem" deploy/nginx/certs/privkey.pem

sed "s/__DOMAIN__/$DOMAIN/g" deploy/nginx/hostinger-ssl.conf.template \
  > deploy/nginx/generated/default-ssl.conf

echo "==> Updating .env.production for HTTPS..."
# Backup once
cp -a .env.production ".env.production.bak.$(date +%Y%m%d%H%M%S)"

set_kv() {
  local key="$1" val="$2"
  if grep -q "^${key}=" .env.production; then
    sed -i "s|^${key}=.*|${key}=${val}|" .env.production
  else
    echo "${key}=${val}" >> .env.production
  fi
}

HOSTS="$DOMAIN"
[[ -n "$VPS_IP" ]] && HOSTS="$HOSTS,$VPS_IP"
set_kv ALLOWED_HOSTS "$HOSTS,localhost,127.0.0.1"
set_kv CORS_ALLOWED_ORIGINS "https://$DOMAIN"
set_kv CSRF_TRUSTED_ORIGINS "https://$DOMAIN"
set_kv INSECURE_HTTP_PILOT "false"
set_kv SECURE_SSL_REDIRECT "true"
set_kv SECURE_HSTS_SECONDS "31536000"
set_kv USE_X_FORWARDED_HOST "true"
set_kv NGINX_CONF_PATH "./deploy/nginx/generated/default-ssl.conf"
set_kv HTTPS_PORT "443"
set_kv COMPOSE_HTTPS "1"

chmod 600 .env.production

echo "==> Starting stack with TLS..."
"${COMPOSE[@]}" up -d --build web backend celery-worker celery-beat

echo "==> Deploy security check..."
"${COMPOSE[@]}" exec -T backend python manage.py check_deploy_security || true

echo ""
echo "=============================================="
echo " HTTPS: https://${DOMAIN}/"
echo " Renew certs: certbot renew (add cron — see docs)"
echo "=============================================="
