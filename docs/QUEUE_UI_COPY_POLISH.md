# Fila de atendimento — polish de copy (apresentação)

**Data:** 2026-08-20  
**Âmbito:** apenas UI/copy da fila. Sem alterações de backend, API, lógica ou dados.

---

## Significado confirmado de «Alta»

No código, o badge «Alta» vinha de `QueuePriority.HIGH` (`PriorityBadge` / `QUEUE_PRIORITY_LABELS`).

**Não** é alta médica (conclusão de episódio).  
**É prioridade da fila.**

Copy nova: **Prioridade alta**.

---

## Shorthand encontrado → copy nova

| Anterior | Nova | Onde |
|---|---|---|
| `#1`, `#2`, … | `1.º na fila`, `2.º na fila`, … | Preview da fila; coluna Posição na tabela |
| `~15 min` | `cerca de 15 min` | Tempo estimado |
| `~60 min` | `cerca de 1 h` | Idem |
| `~90 min` | `cerca de 1 h 30 min` | Idem |
| `~120 min` | `cerca de 2 h` | Idem |
| `PAC-…` (mesmo peso visual que o nome) | `Utente: PAC-…` (secundário, mono) | Preview e tabela |
| `Alta` | `Prioridade alta` | `PriorityBadge` |
| `Baixa` / `Normal` | `Prioridade baixa` / `Prioridade normal` | Consistência no mesmo badge |
| `Em triagem / chamado` | `Chamado` | Estado `CALLED` (um único estado de fila) |
| `Amarelo` / `Verde` / `Vermelho` (só cor) | `Triagem amarela` / `Triagem verde` / `Triagem vermelha` | Badge na fila (`TriageBadge`) |
| `Tempo de espera:` | `Espera:` | `UI_COPY.reception.waitLabel` |
| Motivo na mesma linha com `·` | Linha `Consulta: …` | Preview |

Não removidos: tipografia/identificadores `PAC-…`; cores de triagem (continuam com texto).

---

## Estados (sem mudança de semântica)

| Código | Rótulo apresentado |
|---|---|
| `WAITING` | Aguardando |
| `CALLED` | Chamado (antes: «Em triagem / chamado» — misturava dois conceitos; o estado real é chamado) |
| `IN_SERVICE` | Na consulta |
| `COMPLETED` | Concluído |
| `CANCELLED` | Cancelado |

Cores de triagem (`GREEN`/`YELLOW`/`RED`) mantêm o significado clínico de triagem; o rótulo na fila deixa de ser só o nome da cor.

---

## Componentes / ficheiros alterados

- `features/reception/utils/formatQueueDisplay.ts` (**novo**)
- `features/reception/components/ReceptionQueuePreviewList.tsx`
- `features/reception/components/QueueTable.tsx`
- `features/reception/components/PriorityBadge.tsx`
- `features/reception/components/QueueStatusBadge.tsx`
- `features/reception/components/TriageBadge.tsx`
- `constants/reception.ts` (`QUEUE_PRIORITY_LABELS`)
- `constants/uiCopy.ts` (`waitLabel`)

---

## Gates

| Gate | Resultado |
|---|---|
| `npm run build` | **OK** |
| `npm run lint` | **OK** — 0 erros, 10 avisos pré-existentes |
