#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

npm run start:bg
npm run ready

echo ""
echo "=== SGCS pronto ==="
echo "  UI:          http://localhost:5173"
echo "  API:         http://localhost:8000/api/docs/"
echo "  Login demo:  admin@sauvida.gw / Demo@2026!  (ver docs/DEMO_DATA.md)"
echo "  Parar:       npm run stop"
