# SGCS — Auditoria UI/UX e consistência (frontend)

Documento de referência para o sprint de refinamento visual e de copy. **Sem alterações de API, modelos ou RBAC.**

## Fase 1 — Achados principais (pré-refino)

### Tipografia

| Aspecto | Situação encontrada |
|--------|---------------------|
| Fonte principal | **Inter** configurada em `index.css` (`--font-sans`) |
| Segunda fonte | **Outfit** como `--font-display` (login e utilitário `.font-display`) — **mistura de famílias** |
| Títulos de página | Padrão dominante `text-2xl font-bold sm:text-3xl`; alternativas `text-lg`, `text-3xl` sem regra |
| Pesos | Uso frequente de `font-bold` em KPIs e títulos; labels com `uppercase` + `tracking-widest` |
| Metadados | `text-xs` / `text-[11px]` / `font-mono` para identificadores (aceitável, mas não documentado) |

### Duplicação de componentes

| Área | `design-system/` | `components/ui/` | Notas |
|------|------------------|------------------|--------|
| Button | Variantes primary/secondary/ghost/danger/outline; `rounded-xl`; sombras | Cópia legada `rounded-lg`, slate hardcoded, sem outline | ~30 ficheiros importam `ui/` |
| Card | `rounded-2xl`, header/footer | `rounded-xl`, padding diferente, `text-lg` no título | |
| Badge | `rounded-lg`, tokens semantic surface | `rounded-full`, slate/green hardcoded | |
| Modal/Input/Dialog | design-system + ui duplicados | | |
| Table | `design-system/Table` + `components/tables/Table` | | |

### Cores e tokens

- Tokens úteis já em `@theme`: `surface`, `text`, `text-muted`, `border`, `primary-*`.
- Uso massivo de **slate-*** em páginas antigas vs **text-text** em páginas novas.
- Gradientes decorativos em `RoleDashboardHero` (múltiplos “tons” por perfil).
- Utilities `glass-card`, hover lift em KPIs — mais “marketing” que operacional.

### Botões

- Hierarquia inconsistente: vários primários na mesma vista (faturação, atendimento).
- `RoleDashboardHero` usa `<button>` nativo, não `Button` do design-system.
- Links com aparência de botão vs `Button` dentro de `Link` (padrão misto).

### Badges e estados

- **design-system Badge**: variantes success/warning/danger/info.
- **Reception**: `PriorityBadge`, `QueueStatusBadge`, `TriageBadge`, spans ad hoc na fila (4+ chips).
- `QUEUE_STATUS_LABELS` vs `QUEUE_OPERATIONAL_LABELS` (textos diferentes para o mesmo estado).
- Triage clínica (GREEN/YELLOW/RED) bem separada; risco de redundância com prioridade NORMAL + triagem.

### Copy (PT)

- `uiCopy.ts` existe mas **muitas páginas não o usam** (títulos inline).
- Receção: texto conversacional (“Olá — pronta para atender?”), repetição de KPIs no hero, “Fila agora”, instruções longas na fila.
- Termos mistos: **Paciente** (nav) vs **Utente** (fluxo receção); **Fila de espera** vs **Fila de atendimento**.
- Estados: maioria alinhada (“A carregar…”, “Tentar novamente”); `ErrorState` título genérico “Ocorreu um erro”.

### Layout e cartões

- `PageHeader` (neutro) vs `RoleDashboardHero` (gradiente grande) no mesmo produto.
- Cards aninhados, sombras e `rounded-2xl` em excesso na fila da receção.
- Padding de página variável (`space-y-6`, `max-w-4xl` só em alguns dashboards).

### Formulários

- `design-system/Input` vs `components/ui/Input`.
- Triagem e pacientes usam design-system + componentes de formulário partilhados (`PhoneInput`, `DisplayDateInput`).

### Tabelas

- `design-system/Table` usado em features; estilos de cabeçalho não centralizados em constante.

### Empty / loading / error

- `LoadingState`, `EmptyState`, `ErrorState`, `Skeleton*` no design-system — **bom núcleo**.
- Algumas páginas ainda usam texto longo ou mensagens em inglês em erros de API (via `getApiErrorMessage`).

---

## Fase 2–3 — Alterações aplicadas neste sprint

### Tokens e tipografia

- **Inter apenas** no bundle global (removida Outfit do CSS).
- Tokens semânticos `--color-success`, `--color-warning`, `--color-danger`, `--color-info` em `@theme`.
- **`constants/typography.ts`**: hierarquia `TYPO` (pageTitle, sectionTitle, cardTitle, body, label, meta).
- **`PageHeader`**: alinhado a `TYPO` (sem uppercase no eyebrow; `font-semibold` no título).

### Primitivos

- **`components/ui/Button|Card|Badge`**: re-exportam design-system (compatibilidade, uma fonte de estilo).
- **`design-system/Button`**: `font-medium` (menos peso visual competindo com conteúdo).
- **`design-system/Card`**: sombra/hover decorativo removido; `rounded-xl`.
- **`KpiCard`**: sem uppercase/tracking; valor `text-2xl font-semibold`; sem hover lift.

### Copy e vocabulário (`uiCopy.ts`)

- Secção **`reception`** e **`states`** para receção e mensagens de estado.
- Nav: **Fila de atendimento** (canónico).

### Receção (prioridade)

- **`ReceptionRoleDashboardPage`**: `PageHeader` “Receção” + ação primária única; KPIs sem badges redundantes; alerta de emergência conciso; removido hero conversacional e links de rodapé redundantes.
- **`ReceptionQueueNowCard`**: título **Fila de atendimento**; empty state operacional; “Abrir fila” no footer.
- **`ReceptionQueuePreviewList`**: lista dividida (sem cards empilhados); hierarquia nome → ID → tempo de espera → tipo visita; **2–3 badges** (`TriageBadge`, `PriorityBadge` só HIGH/EMERGENCY, `QueueStatusBadge`); ações **Continuar** / **Ver utente**.

### Qualidade de código

- Corrigidos erros TypeScript em `InvoiceCreatePage`, `ReceptionWorkflowPage`, `triageSchema` / `TriageCheckInWizard`.
- **`npm run build`**: passa.
- **`npm run lint`**: 0 erros (warnings pré-existentes de react-refresh / hooks).

### Backend

- **Não alterado** neste sprint de UI (alterações anteriores de `queue_preview` permanecem apenas se já estavam no branch).

---

## Fase 4–5 — Páginas ainda por alinhar (recomendações)

1. **Role dashboards** (médico, lab, admin, diretor): substituir ou simplificar `RoleDashboardHero` → `PageHeader` + KPIs como receção.
2. **Títulos de página**: migrar `text-2xl font-bold text-slate-900` → `PageHeader` + `TYPO` (~40 ficheiros).
3. **Cores**: substituir `slate-*` por `text-text` / `text-text-muted` / `border-border` progressivamente.
4. **Terminologia**: decisão documentada — **Utente** no fluxo clínico/receção; **Pacientes** como módulo de cadastro (manter ambos com definição clara) ou unificar gradualmente.
5. **Badges**: usar `PriorityBadge` / `QueueStatusBadge` na `QueueTable` e `WaitingQueuePage`; evitar spans locais.
6. **Formulários**: deprecar `components/ui/Input` nas features; um único `FormField` wrapper (label + erro + Input).
7. **Tabelas**: documentar padrão de cabeçalho (`text-xs font-medium text-text-muted`) no `design-system/Table`.
8. **ErrorState**: título padrão “Não foi possível carregar os dados.”; botão retry com `UI_COPY.actions.retry`.
9. **Faturação / consulta / laboratório**: revisão de copy (“Nova fatura”, passos de atendimento) contra vocabulário canónico.
10. **Login**: já sem Outfit; rever hardcoded hex se quiser 100% tokens primary.

---

## Vocabulário canónico (proposta)

| Conceito | Termo UI |
|----------|----------|
| Pessoa atendida | Utente (fluxo); módulo **Pacientes** |
| Fila receção | Fila de atendimento |
| Continuar fluxo | Continuar |
| Novo fluxo | Iniciar atendimento |
| Ver cadastro | Ver utente / Ver paciente (preferir **Ver utente** na receção) |
| Guardar | Guardar |
| Erro carga | Não foi possível carregar os dados. |
| Retry | Tentar novamente |

---

## Definition of done — estado atual

| Critério | Estado |
|----------|--------|
| APIs / modelos / RBAC | ✓ Não alterados neste sprint |
| Funcionalidade | ✓ Preservada |
| Tipografia consistente | ◐ Fundação (`TYPO`, Inter); páginas legadas pendentes |
| Botões unificados | ◐ design-system + re-export ui |
| Forms / tables | ◐ Parcial; auditoria feita |
| Copy PT profissional | ◐ Receção + uiCopy; resto pendente |
| Build / lint | ✓ Build OK; lint sem erros |
| Relatório final | ✓ Este documento |

---

*Última actualização: sprint de consistência UI — receção e fundações globais.*
