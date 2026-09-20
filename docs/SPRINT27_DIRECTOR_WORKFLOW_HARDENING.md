# Sprint 27 — Director Workflow Hardening

**Data:** 2026-08-25  
**Base:** `docs/DIRECTOR_WORKFLOW_AUDIT.md`  
**Estado:** `DIRECTOR_READY_FOR_UAT`

## Objectivo

Transformar o DIRECTOR num perfil de **supervisão** (não operacional clínico/financeiro de balcão), com painel fiável e sem dependência de `reception.view`.

## Entregue

### Dashboard desacoplado da Receção (P0)

- Novo endpoint: `GET /api/v1/dashboard/director/`
- Permissão: `dashboard.view` apenas (sem `reception.view` / `reception.edit`)
- Serviço: `DirectorDashboardService` — secções isoladas (`ok` / `error`)
- Frontend: `DirectorRoleDashboardPage` deixa de chamar `/dashboard/reception/`

### Resumo financeiro executivo

- Reutiliza exactamente `get_resumo_operacional` (mesmas regras da Receção):
  - **Faturado** → `emitida_em`
  - **Recebido** → `data_pagamento` (pagamentos CONFIRMADO)
  - **Saldo pendente** → saldo monetário aberto das faturas do período (inclui PARCIAL)
  - **Reduções** → `ItemFatura.valor_reducao`
- Secundário: `faturas_com_saldo` (contagem), nunca como “saldo”
- Labels: sem «Receita» enganosa; sem card «Saldo em dívida» como quantidade

### Período

- Selector: Hoje / Esta semana / Este mês / Personalizado
- Personalizado exige `data_inicio` + `data_fim` (400 se omitidos — não cai no mês)
- Rótulo PT: `24/08/2026 a 31/08/2026`

### Operacional / Lab / Stock

- Utentes atendidos = check-ins **COMPLETED** no período
- Consultas / concluídas / em espera (agregados)
- Lab: pendentes, aguardam regularização, aguardam validação, concluídos no período — **sem** valores clínicos
- Stock: baixo / sem / próximos validade / expirados (precedência Sprint 26)
- Serviços: «Serviços faturados» (linhas de fatura; não «mais vendidos»)

### Lucro / despesas

- Removidos do painel executivo do Director
- Nota no UI: despesas/lucro fora do piloto enquanto o fluxo de despesas não estiver validado
- Módulo `finance` preservado; não está no menu DIRECTOR

### RBAC DIRECTOR (P0)

Removido (seed idempotente `python manage.py seed_rbac`):

- billing create/edit/delete/payment/quote
- reception.*
- appointments write/clinical/diagnosis/start/finish/…
- doctors.prescription / treatment / …
- laboratory.results.*
- stock entry/exit/adjust
- patients create/edit/export/print
- finance create/edit/cash/expense
- notifications send/template/settings

Mantido (supervisão):

- patients.view, appointments.view, laboratory.view
- billing.view / receipt / export / print
- finance.view / report / dashboard
- reports.*, dashboard.view
- pharmacy.view, stock.view / history
- doctors.view, notifications.view

Backend devolve **403** nas operações removidas. Frontend esconde botões/links.

### Navegação DIRECTOR

Painel · Relatórios · Faturação (read-only) · Pacientes · Stock  
Sem: consultas clínicas, lab operacional, finance, médico, notificações no menu principal.

### Mobile

- KPIs financeiros em 2 colunas compactas no 1.º ecrã
- Hero reduzido (sem skeleton infinito)
- Erros parciais por secção

### Restauro técnico Sprint 24/25

- `PedidoLaboratorioEstadoFaturacao` + campos `estado_faturacao` / `servico` (migração idempotente `0005`)
- `sinais_vitais_triagem` no prontuário (regressão Sprint 26)
- filtro médico em `listar_resultados(user=…)` no ViewSet

## Testes

`apps/dashboard/tests/test_director_hardening_sprint27.py` — acesso sem reception, financeiro, parcial, histórico migrado, lab/stock, RBAC 403, períodos, isolamento de erros.

## Bases existentes

```bash
python manage.py migrate
python manage.py seed_rbac
```

O `seed_rbac` **substitui** as permissões do perfil DIRECTOR pelas novas (idempotente).

## Não feito (de propósito)

- BI novo / contabilidade / inventar despesas ou lucro
- Alterar workflows Receção / Médico / Lab / Enfermagem aprovados
- Expandir exportação
- Gráficos novos no painel Director
