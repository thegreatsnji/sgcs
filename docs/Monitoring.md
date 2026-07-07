# Monitorização — SGCS

## Health checks

| Endpoint | Função |
|----------|--------|
| `GET /health/` | Status geral |
| `GET /live/` | Liveness |
| `GET /ready/` | Readiness (DB, Redis, Celery, disco, RAM, CPU) |

## HealthService

`core/monitoring/health_service.py` — verificações:

- PostgreSQL + latência (ms)
- Redis
- Celery workers + fila activa
- Espaço em disco
- Memória RSS
- CPU (tempo utilizador)

## Dashboard do sistema

`GET /api/v1/dashboard/system/` e `GET /api/v1/settings/monitoring/` — KPIs actualizados com Celery real.

## Logs

| Ficheiro | Conteúdo |
|----------|----------|
| `application.log` | Aplicação |
| `security.log` | Segurança |
| `audit.log` | Auditoria |
| `errors.log` | Erros |

Rotação automática (10 MB × 5 ficheiros).

## Métricas recomendadas (produção)

- Tempo de resposta `/ready/`
- Taxa de falhas Celery
- Uso de disco em `MEDIA_ROOT`
- Cache hit rate Redis
