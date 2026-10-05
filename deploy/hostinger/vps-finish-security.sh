#!/usr/bin/env bash
# SGCS — verificação pós-instalação no VPS (correr como root em /opt/sgcs).
#   bash deploy/hostinger/vps-finish-security.sh
set -euo pipefail

SGCS_DIR="${SGCS_DIR:-/opt/sgcs}"
cd "$SGCS_DIR"

if [[ ! -f .env.production ]]; then
  echo "ERROR: .env.production not found in $SGCS_DIR"
  exit 1
fi

if [[ -f deploy/hostinger/compose-prod.sh ]]; then
  COMPOSE=(bash deploy/hostinger/compose-prod.sh)
else
  COMPOSE=(docker compose -f docker-compose.prod.yml --env-file .env.production)
fi

warn() { echo "WARN: $*"; }
ok() { echo "OK: $*"; }

echo "==> File permissions"
perm_env="$(stat -c '%a' .env.production 2>/dev/null || stat -f '%OLp' .env.production)"
if [[ "$perm_env" != "600" ]]; then
  warn ".env.production mode is $perm_env (recommended 600)"
  chmod 600 .env.production && ok "fixed .env.production -> 600"
else
  ok ".env.production is 600"
fi

if [[ -d backend/data/private ]]; then
  chmod 700 backend/data/private 2>/dev/null || true
  find backend/data/private -type f -exec chmod 600 {} \; 2>/dev/null || true
  ok "private data dir permissions tightened"
fi

echo ""
echo "==> Container status"
"${COMPOSE[@]}" ps

echo ""
echo "==> Published ports (only sgcs-web should expose 80/443 to the host)"
docker ps --filter 'name=sgcs-' --format 'table {{.Names}}\t{{.Ports}}'

echo ""
echo "==> Django deploy security check"
"${COMPOSE[@]}" exec -T backend python manage.py check_deploy_security || warn "check --deploy reported issues (see above)"

echo ""
echo "==> Health endpoints"
if curl -sf -o /dev/null -w '%{http_code}' http://127.0.0.1/health/ | grep -q 200; then
  ok "/health/ returns 200"
else
  warn "/health/ did not return 200 on localhost"
fi

echo ""
echo "==> Production env flags"
grep -E '^(INSECURE_HTTP_PILOT|SECURE_SSL_REDIRECT|ALLOW_PUBLIC_REGISTRATION|ENABLE_API_DOCS|APP_DEBUG|DJANGO_ADMIN_PATH)=' .env.production || true

if grep -q '^INSECURE_HTTP_PILOT=true' .env.production; then
  warn "INSECURE_HTTP_PILOT=true — OK for IP-only pilot; set false after HTTPS (vps-enable-https.sh)"
fi
if grep -q '^ALLOW_PUBLIC_REGISTRATION=true' .env.production; then
  warn "ALLOW_PUBLIC_REGISTRATION should be false in production"
fi
if grep -q '^ENABLE_API_DOCS=true' .env.production; then
  warn "ENABLE_API_DOCS should be false in production"
fi

echo ""
echo "==> Manual hardening checklist (Hostinger panel + SSH)"
cat <<'EOF'
[ ] Firewall: TCP 22, 80, 443 only (drop other inbound)
[ ] SSH: prefer key login; disable root password when keys work (PermitRootLogin prohibit-password)
[ ] Optional: fail2ban on sshd
[ ] Change all staff passwords from pilot default (Administração → Utilizadores)
[ ] Backup: daily pg_dump off-server (see docs/VPS_SECURITY_AND_GITHUB.md)
[ ] Domain + HTTPS: bash deploy/hostinger/vps-enable-https.sh when DNS A record points here
[ ] GitHub: keep repo PRIVATE until staff roster is removed from git history (see docs)
EOF

echo ""
echo "Done."
