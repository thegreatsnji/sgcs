# Deployment — SGCS

Guia de implantação do Sistema de Gestão Clínica SauVida em ambiente de produção.

## Pré-requisitos

- Docker e Docker Compose
- PostgreSQL 16+
- Redis 7+
- Node.js 20+ (build frontend)
- Python 3.13+ (backend)

## Arranque rápido

```bash
docker compose up -d
docker exec sgcs-backend python manage.py migrate
docker exec sgcs-backend python manage.py seed_rbac
```

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | Ligação PostgreSQL |
| `REDIS_URL` | Ligação Redis |
| `SECRET_KEY` | Chave secreta Django |
| `ALLOWED_HOSTS` | Hosts permitidos |
| `CORS_ALLOWED_ORIGINS` | Origens CORS do frontend |

## Health checks

- `GET /health/` — estado geral
- `GET /live/` — liveness
- `GET /ready/` — readiness (PostgreSQL, Redis, Celery, disco, RAM, CPU, latência DB)

Ver [Monitoring.md](./Monitoring.md) (Sprint 13).

## Dashboard do sistema

- `GET /api/v1/dashboard/system/` — monitorização (requer `settings.system`)
- `GET /api/v1/settings/monitoring/` — métricas detalhadas

## Backups

Backups são criados via API (`POST /api/v1/settings/backups/`). A execução real é delegada a tarefas Celery (stubs preparados).

## Produção

1. Definir `DEBUG=False`
2. Configurar SMTP em `/api/v1/settings/email/`
3. Revisar políticas de segurança em `/api/v1/settings/security/`
4. Activar feature flags conforme módulos necessários
5. Executar `npm run build` e servir `frontend/dist` via nginx ou container dedicado

## Monitorização

O painel de sistema reporta: base de dados, Redis, Celery (stub), disco, memória, CPU, utilizadores e sessões activas.
