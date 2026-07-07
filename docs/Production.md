# Produção — SGCS

## Variáveis de ambiente críticas

```env
APP_ENV=production
APP_DEBUG=false
SECRET_KEY=<chave-segura>
SECURE_HSTS_SECONDS=31536000
SECURE_SSL_REDIRECT=true
LOG_TO_FILES=true
LOG_JSON=true
USE_REDIS=true
CELERY_BROKER_URL=redis://redis:6379/0
STORAGE_BACKEND=local  # ou s3, minio, azure
```

## Deploy

```bash
docker compose up --build -d
docker exec sgcs-backend python manage.py migrate
docker exec sgcs-backend python manage.py seed_rbac
docker exec sgcs-backend python manage.py collectstatic --noinput
```

## Settings

Usar `config.settings.production` em produção.

## Storage

`StorageService` suporta filesystem, S3, MinIO e Azure Blob via `STORAGE_BACKEND`.

## Celery

Tarefas com retry automático (`SGCSBaseTask`) — 3 tentativas, backoff exponencial.

## Checklist

- [ ] HTTPS activo
- [ ] Redis e PostgreSQL saudáveis (`/ready/`)
- [ ] Backups configurados
- [ ] Logs com rotação
- [ ] `pytest` verde (226+)
