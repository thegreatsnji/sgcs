# Sprint 21 Fase 4 — Isolamento financeiro

Os 182 valores históricos existem só em `PatientHistory.metadata` (`preco_original`, `desconto_original`, `valor_liquido_original`).

Não existem linhas `KIND=REGISTO_FINANCEIRO_HISTORICO` extra.

## Contagens operacionais (inalteradas desde o backup pré-apply)

| Objecto | Contagem |
| --- | ---: |
| Fatura | 5 |
| Pagamento | 5 |
| Recibo | 5 |
| MovimentoFinanceiro | 5 |
| Appointment | 8 |
| PedidoLaboratorial | 2 |

Leakage com `import_batch=SAUVIDA-HIST-V1`: **0** em Fatura, Pagamento, Recibo, MovimentoFinanceiro.

## Relatórios SGCS

- Dashboard / estatísticas / caixa usam `Fatura`, `Pagamento`, `Recibo` e `FinanceService.calcular_fluxo_caixa()`.
- «Histórico financeiro» da faturação (`BillingService.historico_financeiro`) lê apenas faturas, orçamentos e recibos do utente.

Consequência: os valores importados **não** entram na receita do dia, caixa actual, saldo de faturação, pagamentos do dia, recibos nem dívida activa.

## Risco residual (sem refactor)

A cronologia clínica do utente pode mostrar o acto histórico (e o montante no metadata, se a UI o exibir). Isso é histórico, não cobrança.

Testes: `TestFinancialAndStockIsolation` em `apps/data_migration/tests/test_historical_fase4.py`.
