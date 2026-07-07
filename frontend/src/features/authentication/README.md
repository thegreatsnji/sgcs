# Feature: Authentication

## Migração planeada

| Legado | Destino |
|--------|---------|
| `src/pages/auth/` | `src/features/authentication/pages/` |
| `src/services/auth/` | `src/features/authentication/services/` |
| `src/types/auth.ts` | `src/features/authentication/types/` |

## Notas

- Endpoints JWT em `/api/v1/auth/` permanecem inalterados.
- Não alterar contratos de login/logout/refresh nesta fase.
