#!/usr/bin/env bash
# SGCS — Script de configuração do ambiente de desenvolvimento

set -e

echo "=== SGCS — Configuração do ambiente ==="

if [ ! -f .env ]; then
  echo "A criar ficheiro .env a partir de .env.example..."
  cp .env.example .env
fi

echo "A iniciar serviços Docker..."
docker compose up -d --build

echo ""
echo "=== Ambiente configurado com sucesso ==="
echo "Frontend:  http://localhost:5173"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/api/docs/"
echo "Admin:     http://localhost:8000/admin/"
