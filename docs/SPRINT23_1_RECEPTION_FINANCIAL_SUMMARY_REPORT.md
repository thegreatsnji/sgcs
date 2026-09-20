# Sprint 23.1 — Resumo financeiro operacional da Receção

**Estado final:** `RECEPTION_FINANCIAL_SUMMARY_READY`  
**Data:** 2026-08-20

---

## 1. O que já existia

| Item | Notas |
|---|---|
| Dashboard Receção | Só fila / espera / atendidos — **sem dinheiro** |
| `GET /dashboard/billing/` | Receita hoje/mês + nº pagamentos hoje (por `data_pagamento`) |
| Relatório reduções | `GET /billing/reports/reducoes/?de=&ate=` |
| Histórico por paciente | Faturado / pago / saldo (all-time) |
| Filtros de período (reports) | Exigem `reports.view` — Receção **não** tem |
| Dashboard Finance | Despesas/lucro — `finance.*` — fora do âmbito |
| Isolamento histórico migrado | `PatientHistory` não cria `Fatura`/`Pagamento` |

Auditoria completa: [`RECEPTION_FINANCIAL_SUMMARY_AUDIT.md`](RECEPTION_FINANCIAL_SUMMARY_AUDIT.md).

## 2. O que faltava

- UI no dashboard da Receção
- Semana e período personalizado
- Total faturado, saldo pendente (FCFA) e reduções no mesmo resumo
- Endpoint de agregação por período sob `billing.view` (sem reports/finance)

## 3. O que foi reutilizado

- Modelos `Fatura`, `Pagamento`, `ItemFatura`
- Permissão existente `billing.view` (RECECIONISTA já a possui)
- `CurrencyDisplay`, `Card`, `DisplayDateInput`, design system
- Dashboard Receção (secção nova, sem página nova)
- Conceito de «recebido» por `data_pagamento` (igual ao dashboard billing)

## 4. O que foi implementado

**Backend**

- `apps/billing/period.py` — resolução hoje / semana / mês / personalizado
- `apps/billing/services/resumo_operacional.py` — agregações SQL
- `GET /api/v1/billing/resumo-operacional/` — `ResumoOperacionalView`

**Frontend**

- `ReceptionFinancialSummary` no `ReceptionRoleDashboardPage`
- `billingService.getOperationalSummary`
- Tipos `OperationalBillingSummary` / `OperationalPeriod`

## 5. Endpoint

```
GET /api/v1/billing/resumo-operacional/
  ?periodo=hoje|semana|mes|personalizado
  &data_inicio=AAAA-MM-DD   # obrigatório se personalizado
  &data_fim=AAAA-MM-DD
```

Permissão: **`billing.view`** (sem novas permissões RBAC).

## 6. Filtros disponíveis

| Modo | Intervalo |
|---|---|
| Hoje | dia local actual |
| Esta semana | segunda → hoje |
| Este mês | dia 1 → hoje |
| Personalizado | data_inicio → data_fim (inclusivo); UI em DD/MM/AAAA |

## 7. Definição de cada métrica

| Métrica | Definição |
|---|---|
| **Total faturado** | `SUM(Fatura.total)` com `emitida_em` no período, excl. `CANCELADA` |
| **Total recebido** | `SUM(Pagamento.valor)` `CONFIRMADO` com **`data_pagamento`** no período |
| **Saldo pendente** | `SUM(max(total − pagos confirmados, 0))` das faturas **emitidas** no período (saldo actual, não snapshot histórico) |
| **Reduções** | `SUM(ItemFatura.valor_reducao)` em faturas emitidas no período (não canceladas) |
| **Pagamentos** | `COUNT` de pagamentos confirmados no período |

Redução ≠ pagamento. Saldo ≠ redução. Fatura ≠ dinheiro recebido.

Pacientes atendidos: **não** incluídos neste resumo (já no KPI operacional do dashboard; evitar métrica inventada no endpoint financeiro).

## 8. RBAC

| Alteração | |
|---|---|
| Novas permissões | **Nenhuma** |
| Endpoint | `billing.view` |
| Finance / reports | **Não** concedidos |
| UI | Só renderiza se `hasPermission("billing.view")` |

Documentado na auditoria **antes** da implementação.

## 9. Isolamento do histórico migrado

Só `Fatura` / `Pagamento` / `ItemFatura`.  
`PatientHistory` (incl. metadata financeira Excel) **não** entra.  
Teste explícito: `test_historico_migrado_excluido`.

## 10. Testes

`apps/billing/tests/test_resumo_operacional.py` — **17 passed**:

hoje, semana, mês, personalizado, pagamento em data ≠ fatura, parcial, redução, múltiplos pagamentos, fatura cancelada, pagamento não confirmado / reembolsado, histórico migrado, rececionista OK, sem permissão 403, personalizado sem datas 400, período vazio = zero.

## 11–12. Gates

| Gate | Resultado |
|---|---|
| `manage.py check` | OK |
| `makemigrations --check` | OK |
| `pytest -q --reuse-db` | **416 passed**, 2 skipped, **2 failed** pré-existentes |
| `npm run build` | OK |
| `npm run lint` | 0 erros, 10 avisos pré-existentes |

### Falhas pré-existentes (fora de âmbito)

1. `TestConsultaFluxo::test_handoff_cria_consulta_em_espera`
2. `TestWaitingQueue::test_assign_to_doctor`  

Causa: médico indisponível. Sem regressões novas.

## 13. Pendências

- **Fecho formal de caixa:** não criado; «Hoje» cobre a verificação do balcão. Melhoria futura só se a clínica exigir fecho assinado.
- UAT presencial: validar números com a rececionista (hoje / semana / personalizado).
- Stock / catálogo / migração: intocados.

---

## Entrega resumida

| Capacidade | |
|---|---|
| Total hoje | SIM |
| Total semana | SIM |
| Total mês | SIM |
| Período personalizado | SIM |
| Total faturado | SIM |
| Total recebido | SIM |
| Saldo pendente | SIM |
| Reduções | SIM |
| Nº pagamentos | SIM |
| Histórico migrado excluído | SIM |
| Receção só métricas operacionais | SIM |
