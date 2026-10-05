# Desempenho em produção (VPS)

Melhorias incluídas no código para **https://clinicasauvida.systems** (ou outro domínio prod).

## O que já está optimizado

| Camada | Medida |
|--------|--------|
| **Frontend** | Rotas lazy (`pages.lazy.ts`), chunks Vite (vendor, charts, reports, …) |
| **Nginx** | Gzip; cache longo em `/assets/` (ficheiros com hash) |
| **Django** | Redis cache; fila receção cacheia IDs (não QuerySet); `CONN_MAX_AGE` em produção |
| **Gunicorn** | Workers configuráveis; recycle periódico (`max-requests`) |
| **Celery** | Concurrency e prefetch via env |
| **Redis** | `maxmemory` + LRU; DBs separados para cache vs Celery (recomendado) |

## Aplicar no VPS (uma vez)

```bash
cd /opt/sgcs
git pull origin main
```

Editar `/opt/sgcs/.env.production` — acrescentar ou ajustar:

```env
REDIS_CACHE_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
DB_CONN_MAX_AGE=120
GUNICORN_WORKERS=3
CACHE_TIMEOUT=300
CELERY_CONCURRENCY=2
```

Se já usa HTTPS com ficheiro gerado `deploy/nginx/generated/default-ssl.conf`, após `git pull` confirme que inclui:

`include /etc/nginx/snippets/sgcs-performance.conf;`

(se não, copie de `hostinger-ssl.conf.template` ou volte a correr `vps-enable-https.sh`).

Rebuild:

```bash
bash deploy/hostinger/compose-prod.sh up -d --build
```

## Ajuste fino (Hostinger KVM 2)

- **RAM apertada:** `GUNICORN_WORKERS=2`, `CELERY_CONCURRENCY=1`
- **Muitos utilizadores em simultâneo:** `GUNICORN_WORKERS=3` (máx. ~5 em 2 vCPU se monitorizar RAM)
- **Relatórios lentos:** normal com PDF/consultas pesadas — Celery trata tarefas async; evite abrir muitos relatórios ao mesmo tempo no piloto

## O que medir

- Tempo de abertura do login e do dashboard (browser DevTools → Network)
- `docker stats` no VPS — CPU/RAM dos contentores `sgcs-backend`, `sgcs-db`, `sgcs-redis`

## Limites do piloto

Um VPS partilhado não substitui escala horizontal. Para dezenas de postos em pico, planear upgrade de plano ou réplica de leitura PostgreSQL (fase posterior).
