# Auditoria — Resumo financeiro operacional da Receção

**Data:** 2026-08-20  
**Âmbito:** Verificar se a Receção já consegue consultar totais por período (hoje / semana / mês / personalizado) sem criar módulo financeiro novo.

---

## Inventário

| Funcionalidade | Existe | Backend | Frontend | Reutilizável | Acção |
|---|---|---|---|---|---|
| Dashboard Receção (fila / espera / atendidos) | Sim | `GET /api/v1/dashboard/reception/` | `ReceptionRoleDashboardPage` | Sim (ops) | Manter; **não** misturar com finanças no mesmo KPI strip sem rótulo claro |
| Receita hoje / mês (pagamentos confirmados) | Sim | `GET /api/v1/dashboard/billing/` → `BillingService.get_dashboard_summary` | `BillingDashboardPage` / Director | Parcial | Reutilizar lógica de agregação; **não** basta sozinho (falta semana, personalizado, faturado, saldo €, reduções) |
| Nº pagamentos hoje | Sim | Mesmo dashboard billing | Billing cards | Parcial | Incluir no resumo por período |
| Faturas pendentes / pagas (contagem) | Sim | Dashboard billing | Billing / Director | Parcial | «Saldo em dívida» no Director = **contagem** de faturas, não valor FCFA |
| Relatório de reduções (de/até) | Sim | `GET /api/v1/billing/reports/reducoes/?de=&ate=` | Sem UI na Receção | Sim (agregação) | Reutilizar cálculo de `valor_reducao`; filtrar por data adequada |
| Histórico financeiro por paciente | Sim | `GET /api/v1/billing/patient-history/<id>/` | `PatientHistoryPage` | Sim (paciente) | Não substitui resumo do balcão |
| Filtros de período (hoje/semana/mês/personalizado) | Sim | `reports/filters.parse_report_filters` | `ReportFilter` | Parcial | Relatórios exigem `reports.view` — **Receção não tem**; reutilizar padrão de query, não o módulo reports |
| Dashboard Financeiro (receita/despesa/lucro) | Sim | `GET /api/v1/dashboard/finance/` | `FinanceDashboardPage` | Não | Bloqueado RBAC (`finance.*`); traz despesas/lucro — fora do âmbito Receção |
| Relatórios executivos / billing reports | Sim | `/api/v1/reports/...` | Reports pages | Não | Exigem `reports.*` |
| Fecho diário de caixa | Conceito caixa | `finance/cash-registers/.../close/` | Finance | Não | Não criar módulo; «Hoje» no resumo operacional cobre verificação do balcão |
| Resumo financeiro no dashboard Receção | **Não** | — | — | — | **Implementar** |
| Endpoint billing com período custom (SUM faturado/recebido/saldo/reduções) | **Não** | Dashboard só hoje+mês | — | — | **Criar** endpoint mínimo sob `billing.view` |
| List filters de fatura/pagamento por data | Parcial | Só paciente/estado | — | Fraco | Preferir agregação no endpoint novo |

---

## Definições já usadas no código

| Métrica | Fonte actual | Data usada |
|---|---|---|
| Receita / recebido (billing dashboard) | `SUM(Pagamento.valor)` `estado=CONFIRMADO` | **`data_pagamento`** (correcto para «recebido») |
| Faturas emitidas hoje | `COUNT(Fatura)` excl. canceladas | `emitida_em` |
| Reduções (relatório) | `ItemFatura.valor_reducao` | Filtro actual por `fatura.emitida_em` |
| Histórico migrado | `PatientHistory` metadata | **Não** cria `Fatura`/`Pagamento` (Sprint 21 Fase 4) |

---

## RBAC

| Permissão | RECECIONISTA | Relevância |
|---|---|---|
| `billing.view` | Sim | Suficiente para resumo operacional |
| `billing.payment` / `create` / `receipt` | Sim | Trabalho do balcão |
| `finance.*` | Não | Não conceder |
| `reports.*` | Não | Não conceder |

**Decisão RBAC:** novo endpoint sob `billing.view` apenas. Sem novas permissões administrativas. Sem acesso a despesas/lucro/caixa.

---

## Lacunas vs necessidade da Receção

| Necessidade | Estado |
|---|---|
| Total hoje | Parcial (`receita_hoje` = recebido; falta faturado/saldo/reduções no mesmo sítio) |
| Total semana | **Falta** |
| Total mês | Parcial (`receita_mensal` = recebido) |
| Período personalizado | **Falta** |
| Total faturado (período) | **Falta** no dashboard |
| Total recebido (por data pagamento) | Existe só hoje/mês |
| Saldo pendente (valor FCFA) | **Falta** (só contagem de faturas) |
| Reduções (soma) | Existe relatório separado; **falta** no resumo Receção |
| Nº pagamentos | Existe só hoje |
| UI no dashboard Receção | **Falta** |
| Isolamento histórico migrado | Já garantido nas queries Fatura/Pagamento |

---

## Decisão de implementação (após auditoria)

1. **Onde:** secção «Resumo financeiro» no `ReceptionRoleDashboardPage` (não página nova).
2. **Backend:** endpoint novo mínimo, ex. `GET /api/v1/billing/resumo-operacional/?periodo=...` com agregação SQL (`SUM`/`COUNT`), permissão `billing.view`.
3. **Reutilizar:** modelos `Fatura`/`Pagamento`/`ItemFatura`, padrão de datas dos reports (sem exigir `reports.view`), `CurrencyDisplay` / design system.
4. **Não reutilizar:** dashboard finance, reports executivos, fecho de caixa, PatientHistory.
5. **Fecho formal de caixa:** melhoria futura opcional; «Hoje» cobre a verificação operacional do balcão.

---

## Estado da auditoria

**AUDITORIA_CONCLUIDA** — implementação concluída em Sprint 23.1.

Ver [`SPRINT23_1_RECEPTION_FINANCIAL_SUMMARY_REPORT.md`](SPRINT23_1_RECEPTION_FINANCIAL_SUMMARY_REPORT.md).

| Item da tabela acima | Resultado pós-implementação |
|---|---|
| Resumo financeiro no dashboard Receção | **Implementado** (`ReceptionFinancialSummary`) |
| Endpoint billing com período custom | **Implementado** `GET /api/v1/billing/resumo-operacional/` |
| RBAC | Sem permissões novas; usa `billing.view` |
