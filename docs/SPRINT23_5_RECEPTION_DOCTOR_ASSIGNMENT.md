# Sprint 23.5 — Atribuição de médico (Receção)

**Data:** 2026-08-20  
**Base:** `RECEPTION_READY_FOR_UAT`  
**Estado:** `RECEPTION_DOCTOR_ASSIGNMENT_READY`

---

## Objectivo

Tornar a escolha do médico **explícita** pela Receção no fluxo existente (sem módulo novo, sem segunda fila, sem auto-assignment).

---

## Alterações

### Backend

- `assign_to_doctor` exige `doctor_id`
- Mensagem de indisponibilidade alinhada ao UAT
- Reatribuição segura antes de `EM_CONSULTA` (mesmo check-in/consulta)
- Opções: `availability_label`, `scheduled_doctor`, sem sugestão por menor fila
- Fila: `assigned_doctor`, `can_reassign_doctor`
- Filtros: `doctor`, `unassigned`

### Frontend

- Painel passo 4: escolha explícita; pré-selecção só de médico da marcação
- Fila: coluna médico + modal de atribuição/alteração + filtro

### Testes

`apps/reception/tests/test_reception_doctor_assignment.py`

### Docs

- `docs/RECEPTION_DOCTOR_ASSIGNMENT.md`
- Actualização UAT presencial (cenário 16)

---

## Gates

| Gate | Resultado |
|---|---|
| `python manage.py check` | OK (0 issues) |
| `makemigrations --check` | OK (No changes detected) |
| `pytest -q --reuse-db` | **475 passed**, 2 skipped, 0 failed |
| `npm run build` | OK |
| `npm run lint` | 0 errors, 10 warnings (pré-existentes) |

Baseline anterior: 464 passed. Novos testes de atribuição incluídos; sem regressões.
