# Features — Arquitetura por domínio (SGCS)

Estrutura preparada para migração gradual do código existente em `src/pages/`, `src/services/` e `src/components/`.

## Princípio

Cada feature agrupa **páginas**, **componentes**, **hooks**, **serviços** e **tipos** do respetivo domínio.

```
src/features/<domínio>/
├── components/     # UI específica do domínio
├── hooks/          # Hooks React Query / estado local
├── pages/          # Páginas da feature
├── services/       # Chamadas API
├── types/          # Tipos TypeScript
└── README.md       # Guia de migração da feature
```

## Features

| Pasta | Origem atual (legado) | Estado |
|-------|----------------------|--------|
| `authentication/` | `pages/auth/`, `services/auth/` | Estrutura criada |
| `users/` | `pages/admin/Users*`, `services/users/` | Estrutura criada |
| `dashboard/` | `pages/admin/Dashboard`, `services/dashboard/` | Estrutura criada |
| `settings/` | — | Preparada para configurações |
| `patients/` | `apps/patients` (backend) | **Implementada** (Sprint 4) |
| `appointments/` | `apps/appointments` (backend) | Preparada |
| `laboratory/` | `apps/laboratory` (backend) | Preparada |
| `billing/` | `apps/billing` (backend) | Preparada |

## Regras de migração

1. **Não remover** ficheiros legados até a feature estar 100% migrada.
2. Re-exportar temporariamente de locais antigos se necessário (padrão já usado em `services/api.ts`).
3. Uma feature de cada vez; começar por `users` e `dashboard` (já implementados).
4. Novos componentes base devem vir de `src/design-system/`.

## Exemplo de importação futura

```tsx
import { UsersPage } from "@/features/users/pages/UsersPage";
import { Button } from "@/design-system";
```
