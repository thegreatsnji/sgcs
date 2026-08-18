# Sprint 21 Fase 3 — Contagens de BD

**Ambiente:** development, PostgreSQL `sgcs` @ `sgcs-db`  
**Batch:** `SAUVIDA-HIST-V1`

## Antes de qualquer apply

| Tabela | Contagem |
| --- | ---: |
| Patient | 10 |
| PatientHistory | 10 |
| User | 12 |
| Appointment | 8 |
| Fatura | 5 |
| Pagamento | 5 |
| Recibo | 5 |
| PedidoLaboratorial | 2 |
| MedicamentoUrgencia | 9 |
| MovimentoStockUrgencia | 0 |
| MovimentoFinanceiro | 5 |

Pacientes `MIGRACAO_EXCEL_SAUVIDA` / `SAUVIDA-HIST-V1`: 0.

## Depois de `--patients-only`

| Tabela | Contagem | Δ vs antes |
| --- | ---: | ---: |
| Patient | 166 | +156 |
| PatientHistory | 166 | +156 (`REGISTO` de importação) |
| User | 12 | 0 |
| Appointment | 8 | 0 |
| Fatura | 5 | 0 |
| Pagamento | 5 | 0 |
| Recibo | 5 | 0 |
| PedidoLaboratorial | 2 | 0 |
| MedicamentoUrgencia | 9 | 0 |
| MovimentoStockUrgencia | 0 | 0 |
| MovimentoFinanceiro | 5 | 0 |

Pacientes id 1–10 (SGCS pré-existentes) intactos. Importados: id 11–166.

## Depois de `--history-only` (estado final)

| Tabela | Contagem | Δ vs pós-pacientes | Δ vs início |
| --- | ---: | ---: | ---: |
| Patient | 166 | 0 | +156 |
| PatientHistory | 348 | +182 | +338 |
| User | 12 | 0 | 0 |
| Appointment | 8 | 0 | 0 |
| Fatura | 5 | 0 | 0 |
| Pagamento | 5 | 0 | 0 |
| Recibo | 5 | 0 | 0 |
| PedidoLaboratorial | 2 | 0 | 0 |
| MedicamentoUrgencia | 9 | 0 | 0 |
| MovimentoStockUrgencia | 0 | 0 | 0 |
| MovimentoFinanceiro | 5 | 0 | 0 |

`PatientHistory` +338 = 156 eventos `REGISTO` (criação do utente importado) + 182 eventos clínicos. Os 10 históricos SGCS originais permanecem.

## Esperado vs observado

- Patient aumenta só pelos 156 importados: **sim**
- PatientHistory clínico aumenta só pelos 182 eventos prontos: **sim**
- Restantes tabelas operacionais inalteradas: **sim**
- Stock inalterado: **sim**
