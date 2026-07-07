# Performance — SGCS

## Optimização de queries

- `select_related()` e `prefetch_related()` aplicados em pacientes, consultas, laboratório, faturação e financeiro.
- Paginação padronizada via `StandardPagination` (máx. 100 por página).

## Cache Redis

Helper central: `core/cache/cache_helper.py`

| Namespace | TTL (seg) | Variável env |
|-----------|-----------|--------------|
| Dashboard | 120 | `CACHE_TTL_DASHBOARD` |
| Pacientes | 120 | `CACHE_TTL_PATIENTS` |
| Relatórios | 120 | `CACHE_TTL_REPORTS` |
| Financeiro | 60 | `CACHE_TTL_FINANCE` |
| Billing | 60 | `CACHE_TTL_BILLING` |
| Settings | 300 | `CACHE_TTL_SETTINGS` |

Invalidação: `CacheHelper.delete(namespace, key)` ou `invalidate_namespace()`.

## Índices

Índices existentes em `patients`, `appointments` e módulos críticos — ver migrations.

## Frontend

- Code splitting Vite (`vendor`, `query`)
- React Query `staleTime: 60s`
- `React.lazy` + `Suspense` preparados em `routes/lazyRoutes.tsx`
