# Sprint 23.2 — Hardening Faturação (Receção)

**Data:** 2026-08-20  
**Base:** `docs/RECEPTION_BILLING_AUDIT.md`  
**Estado:** `RECEPTION_BILLING_READY`

---

## Objectivo

Fechar lacunas operacionais e o risco de overpayment na Faturação da RECECIONISTA, sem módulo financeiro novo nem anulação de pagamentos.

---

## Overpayment (crítico)

| | |
|---|---|
| Problema | `registar_pagamento` aceitava valor > saldo |
| Correcção | `BillingService._validar_valor_pagamento` — valor ≤ saldo disponível |
| Saldo disponível | `total − (PENDENTE + PROCESSADO + CONFIRMADO)` |
| Confirmação | Revalida com `select_for_update` antes de confirmar |
| Mensagem | «O valor do pagamento não pode ser superior ao saldo da fatura.» |
| Frontend | `PaymentForm` com `max` / validação + aviso do saldo |

Pagamentos históricos não foram alterados.

---

## Pesquisa e filtros

API `GET /billing/invoices/`:

| Parâmetro | Efeito |
|---|---|
| `search` | Número fatura, nome utente, n.º processo |
| `estado` | PENDENTE / PARCIAL / PAGA / CANCELADA |
| `periodo` | hoje / semana / mes / personalizado (+ `data_inicio`/`data_fim`) |
| `com_saldo` | Faturas cobráveis com saldo > 0 |

UI lista: pesquisa debounced, filtros estado/período, checkbox «Com saldo pendente», colunas Total/Pago/Saldo + «Ver fatura».

---

## Cancelar fatura

- Reutiliza `POST /billing/invoices/{id}/cancel/` (`billing.edit` — já no seed Receção)
- UI no detalhe com confirmação; soft `CANCELADA`
- Não aparece em `com_saldo`; resumo operacional exclui canceladas (regra existente)
- **Anulação de pagamento:** deliberadamente **não** implementada

---

## Deep-link Atendimento rápido

| Query | Comportamento |
|---|---|
| `paciente` | Mantido; **bloqueado** se veio com `retorno` (fluxo atendimento) |
| `tipo=CONSULTA\|CONTROLE` | Mapeia para código exacto `CONS-GERAL` / `CONS-CONTROLE` — **sugestão** com confirmação, sem auto-add |

Sem fuzzy matching. Criação manual de fatura inalterada (paciente editável).

---

## Labels

Métodos e estados de pagamento usam `formatBilling.ts` (Dinheiro, Transferência, … / Pendente, Confirmado, …). Histórico mostra `FAT-…` / estados em PT. Tab Paciente → histórico com `?paciente=`.

---

## RBAC

Sem novas permissões. Cancelar usa `billing.edit` existente. Sem `finance.*`, sem delete de pagamentos.

---

## Testes

`apps/billing/tests/test_reception_billing_hardening.py`:

- pagamento exacto / parcial+exacto
- overpay / zero / negativo
- pendente reserva saldo
- redução + parcial + overpay
- search / com_saldo / período hoje
- cancelar + exclusão de saldo / resumo
- cancelar paga recusado

---

## Pendências (fora de âmbito)

- Anulação/estorno de pagamento — requer fluxo próprio de auditoria e autorização.
- Pré-selecção automática de serviço (mantida como sugestão confirmável).
- Remoção de item pós-emissão (API inexistente).

---

## Gates

| Gate | Resultado |
|---|---|
| `manage.py check` | OK |
| `makemigrations --check` | OK (sem migrações) |
| Hardening + resumo | 27 passed |
| Suite completa | **434 passed**, 2 skipped, **2 failed** pré-existentes (médico indisponível em handoff — fora de âmbito) |
| `npm run build` | OK |
| `npm run lint` | 0 errors (warnings pré-existentes) |
