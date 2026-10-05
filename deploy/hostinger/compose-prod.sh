#!/usr/bin/env bash
# Wrapper: docker compose prod (+ HTTPS override quando TLS está activo).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
ENV_FILE="${ENV_FILE:-.env.production}"
FILES=(-f docker-compose.prod.yml)
if [[ -f "$ENV_FILE" ]] && grep -q 'default-ssl.conf' "$ENV_FILE" 2>/dev/null; then
  FILES+=(-f docker-compose.prod.https.yml)
fi
exec docker compose "${FILES[@]}" --env-file "$ENV_FILE" "$@"
