# Guia de UI/UX — SGCS SauVida

## Princípios

1. **Português em toda a interface** — menus, botões, erros, toasts, breadcrumbs.
2. **Moeda FCFA** — usar `CurrencyDisplay` / `formatCurrencyAmount`.
3. **Um trabalho por ecrã** — cabeçalho claro (`PageHeader`), acções principais evidentes.
4. **Consistência** — preferir `design-system/` em ecrãs novos; `components/ui` mantém re-exports de compatibilidade.
5. **Sem alterações de contrato** — UI não altera endpoints, JWT, modelos nem regras de negócio.

## Design system

Localização: `frontend/src/design-system/`

Componentes-chave: Button, Input, Card, Badge, Avatar, Modal, Table, Pagination, EmptyState, ErrorState, LoadingState, Skeleton, Toast, CurrencyDisplay.

Compatibilidade: `frontend/src/components/ui/index.ts` reexporta aliases `DesignSystem*` onde as APIs diferem.

## Layout da aplicação

- `AppShell` + `AppSidebar` (recolhível) + `TopHeader`
- Menus por perfil: `frontend/src/constants/navigation.ts` + `UI_COPY`
- Breadcrumbs: `Breadcrumbs.tsx`
- Landing pós-login: `getRoleDashboardPath` em `utils/roleRouting.ts`

## Impressão

Shell reutilizável: `frontend/src/components/print/PrintDocument.tsx`

Wrappers: ficha do paciente, receita, resultado laboratorial, fatura, recibo.

CSS: `frontend/src/styles/print.css` (importado em `main.tsx`).

## Responsividade

- Desktop / laptop: tabelas densas
- Tablet (prioridade clínica/receção): cartões e alvos tácteis ≥ 44px
- Telemóvel: tabelas → cartões ou scroll horizontal controlado

## Acessibilidade

- Labels associados a campos
- Foco visível
- Mensagens de erro ligadas aos inputs
- Contraste adequado ao tema claro/escuro

## Copy

Fonte central de textos: `frontend/src/constants/uiCopy.ts`

Evitar strings em inglês na UI; identificadores de código podem permanecer em inglês.
