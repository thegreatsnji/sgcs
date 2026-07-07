# Design System SGCS

Biblioteca de componentes base do SGCS, preparada para migração gradual a partir de `src/components/ui/`.

## Componentes

| Componente | Ficheiro | Uso |
|------------|----------|-----|
| Button | `Button.tsx` | Ações primárias e secundárias |
| Input | `Input.tsx` | Campos de formulário com label/erro |
| Card | `Card.tsx` | Contentores com header/footer |
| Modal | `Modal.tsx` | Diálogos de confirmação |
| Table | `Table.tsx` | Tabelas genéricas tipadas |
| Badge | `Badge.tsx` | Estados e etiquetas |
| Avatar | `Avatar.tsx` | Perfil com iniciais ou imagem |
| Toast | `Toast.tsx` | Notificações temporárias |
| Pagination | `Pagination.tsx` | Navegação de páginas |
| EmptyState | `EmptyState.tsx` | Listas vazias |
| LoadingState | `LoadingState.tsx` | Estados de carregamento |
| ErrorState | `ErrorState.tsx` | Falhas recuperáveis |

## Importação

```tsx
import { Button, Card, Table } from "@/design-system";
```

## Migração

1. Novos ecrãs devem importar de `src/design-system/`.
2. Componentes legados em `src/components/ui/` permanecem até migração completa.
3. Não remover ficheiros existentes nesta sprint.
