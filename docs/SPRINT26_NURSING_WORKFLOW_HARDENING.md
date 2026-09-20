# Sprint 26 — Nursing Workflow Hardening

**Data:** 2026-08-24  
**Base:** `docs/NURSING_WORKFLOW_AUDIT.md`  
**Estado alvo:** `NURSING_READY_FOR_UAT`

## Objectivo

Hardening focado do perfil **ENFERMEIRO** sem criar módulo novo: isolar da Receção, corrigir RBAC, validade de stock, expor Ajuste/Perda, stock inicial e duplicado exacto. Preservar triagem e sinais vitais. **Não** implementar notas/procedimentos/administração de medicamento.

## Decisões

### Receção vs Enfermagem

- ENFERMEIRO mantém **apenas** `reception.create` (check-in/triagem).
- Removidos do seed: `reception.view`, `reception.edit`, `appointments.edit`.
- UI: menu sem fila, atendimento, exames lab, consultas. Rotas `/reception/*` só RECECIONISTA/ADMINISTRADOR.
- **Decisão clínica pendente:** quem é o responsável principal pela triagem — Receção ou Enfermagem? Ambos podem triar nesta sprint (validar presencialmente).

### Regularização lab (P0)

- `mark_lab_order_billed` exige **AND** `reception.edit` + `billing.edit`.
- ENFERMEIRO → 403. Receção continua autorizada. Lab inalterado (Sprint 25).

### Appointments

- Triagem não precisa de `appointments.edit`.
- PATCH consulta / SOAP / diagnóstico / plano / prescrição / médico atribuído: 403 para ENFERMEIRO.
- Médico continua a ver `sinais_vitais_triagem` sem copiar o registo original.

### Stock — validade

Precedência visual/API:

1. EXPIRADO  
2. SEM_STOCK  
3. PROXIMO_DA_VALIDADE  
4. STOCK_BAIXO  
5. DISPONIVEL (Normal)

Quantidade > 0 e validade passada → **Expirado**, nunca «Sem stock» nem «Disponível».  
Saída clínica bloqueada (backend + UI): «Este item está expirado e não pode ser utilizado.»  
Perda/Expiração e Ajuste permitidos.

### Ajuste / Perda

API já existia. UI em modais na linha do item (`Mais acções`). Movimentos auditados; saldo **nunca** editado directamente. Motivo obrigatório.

### Stock inicial

Item com quantidade 0 e sem entradas → «Stock inicial por confirmar» → acção **Definir stock inicial** (movimento ENTRADA, idempotente).

### Duplicados

Correspondência exacta `nome` + `apresentação` (iexact). Sem fuzzy merge. API 400 + `existing_id`.

### Fotos / Excel

Fotos continuam referência. `CX/50` não é saldo. Texto original não é mostrado na UI. Sem importação Excel nesta sprint.

### Prescrição → stock

Sem redução automática. Médico prescreve; enfermeiro faz Saída se o item for usado.

### Notas / procedimentos

**DECISÃO_CLINICA_PENDENTE.** Não implementado. Perguntar no UAT (curativos, injecções, soroterapia, administração, nota de enfermagem).

## Alterações principais

| Área | Ficheiros |
|---|---|
| RBAC seed | `apps/users/management/commands/seed_rbac.py` |
| Lab billed AND | `apps/reception/permissions.py`, `RBACService.user_has_all_permissions` |
| Stock estados/serviço | `apps/pharmacy/status.py`, `stock_service.py`, `views.py`, `serializers.py` |
| FE enfermeiro | `NurseRoleDashboardPage`, `NurseTriagePage`, `navigation.ts`, `routes/index.tsx` |
| FE stock | `UrgentStockPage`, `UrgentStockHistoryPage`, `pharmacy.service.ts` |
| FE triagem copy | `TriageCheckInWizard.tsx` |
| Testes | `apps/pharmacy/tests/test_nursing_hardening_sprint26.py` |

## Ambientes existentes

Reexecutar `python manage.py seed_rbac` para aplicar o perfil ENFERMEIRO actualizado (o comando faz `permissions.clear()` + `set`).

## Gates

- `python manage.py check` — 0 issues
- `python manage.py makemigrations --check` — No changes detected
- `pytest -q --reuse-db` — **525 passed**, 2 skipped, 0 failed
- `npm run lint` — 0 errors (warnings pré-existentes)
- `npm run build` — OK

## UAT

Ver `docs/UAT_ENFERMAGEM_FINAL.md`.
