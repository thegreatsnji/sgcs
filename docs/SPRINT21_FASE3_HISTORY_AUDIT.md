# Sprint 21 Fase 3 — Auditoria pós-histórico

**Data:** 2026-08-17  
**Batch:** `SAUVIDA-HIST-V1`  
**Actor:** `admin@sauvida.gw`  
**Resultado:** **APROVADO**

## Apply (`--history-only --skip-blocked`)

| Indicador | Valor |
| --- | --- |
| Pacientes criados nesta etapa | 0 |
| PatientHistory clínicos criados | 182 |
| Consultas | 111 |
| Controlos | 16 |
| Laboratório estruturado (`ALINHADO`) | 4 |
| Laboratório textual | 39 |
| Ecografias | 8 |
| Cirurgias | 4 |
| Eventos bloqueados importados | 0 |
| Eventos sem paciente importados | 0 |
| Datas bloqueadas importadas | 0 |
| `historico_id` duplicados | 0 |
| Ligação `migration_id` paciente | 182/182 |
| `medico_sgcs` preenchido | 0 (todos `null`) |
| Eventos com `medico_original` | 4 |
| Valores históricos no metadata | 182 |
| Registos `KIND=REGISTO_FINANCEIRO_HISTORICO` extra | 0 |

Proveniência em todos os 182: `source=MIGRACAO_EXCEL_SAUVIDA`, `source_sheet`, `source_row`, `import_batch=SAUVIDA-HIST-V1`, `imported_at`, `imported_by=admin@sauvida.gw`, descrição original, datas.

## Isolamento operacional (sem variação nesta etapa)

| Objecto | Antes history-only | Depois |
| --- | --- | --- |
| Patient | 166 | 166 |
| Fatura | 5 | 5 |
| Pagamento | 5 | 5 |
| Recibo | 5 | 5 |
| MovimentoFinanceiro | 5 | 5 |
| PedidoLaboratorial | 2 | 2 |
| MedicamentoUrgencia | 9 | 9 |
| MovimentoStockUrgencia | 0 | 0 |
| Appointment | 8 | 8 |

Nenhuma factura, pagamento, recibo, movimento de caixa ou stock criado. Nenhum resultado laboratorial inventado. Pedidos laboratoriais modernos inalterados.

## Financeiro histórico

Os 182 valores aparecem só em `PatientHistory.metadata` (`preco_original` / `valor_liquido_original`).

Relatórios de receita, caixa e «histórico financeiro» de faturação leem `Fatura` / `Pagamento` / `Recibo` / `MovimentoFinanceiro` — **não** misturam estes valores. Saldo actual e pagamentos do dia inalterados.

**Risco residual (sem refactor nesta fase):** a ficha clínica do utente mostra os eventos históricos (incluindo montantes no metadata, se a UI os exibir). Não contam como cobrança activa.

## Laboratório histórico

4 exames com mapeamento estruturado; 39 textuais; ambíguos não importados. Sem `PedidoLaboratorial` novo.

## Médicos

3 médicos históricos continuam sem utilizador SGCS. `medico_original` preservado; `medico_sgcs` nulo. Nenhuma conta criada.

## Stock

55 candidatos **não** importados. `quantidade_inicial` vazia. Movimentos de stock inalterados.
