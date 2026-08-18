# Sprint 21 Fase 3 — Auditoria pós-pacientes

**Data:** 2026-08-17  
**Batch:** `SAUVIDA-HIST-V1`  
**Actor:** `admin@sauvida.gw`  
**Resultado:** **APROVADO** — history-only autorizado.

## Apply (`--patients-only --skip-blocked`)

| Indicador | Valor |
| --- | --- |
| Pacientes criados | 156 |
| Pacientes actualizados / associados | 0 |
| Pacientes reutilizados (1.ª execução) | 0 |
| Pacientes ignorados (bloqueados, não escritos) | 38 |
| Pacientes bloqueados importados | 0 |
| Duplicados técnicos (`migration_id`) | 0 |
| Pacientes sem nome válido criados | 0 |
| Merge automático | não |
| Stock | não processado |

## Proveniência (156 importados)

- `source` = `MIGRACAO_EXCEL_SAUVIDA`
- `import_batch` = `SAUVIDA-HIST-V1`
- `migration_id` único e não vazio
- `dados_verificados` = `false` (0 confirmados)
- `created_by` = `admin@sauvida.gw`
- `record_class` histórico

## Comparação BD (pacientes)

| Tabela | Antes | Depois | Δ |
| --- | --- | --- | --- |
| Patient | 10 | 166 | +156 |
| PatientHistory | 10 | 166 | +156 (eventos `REGISTO` de importação; **0** eventos clínicos) |
| User | 12 | 12 | 0 |
| Appointment | 8 | 8 | 0 |
| Fatura | 5 | 5 | 0 |
| Pagamento | 5 | 5 | 0 |
| Recibo | 5 | 5 | 0 |
| PedidoLaboratorial | 2 | 2 | 0 |
| MedicamentoUrgencia | 9 | 9 | 0 |
| MovimentoStockUrgencia | 0 | 0 | 0 |
| MovimentoFinanceiro | 5 | 5 | 0 |

Pacientes SGCS pré-existentes (id 1–10): intactos, sem `source=MIGRACAO_EXCEL_SAUVIDA`. Importados: id 11–166.

## Pacientes incompletos

Telefone/residência/data de nascimento/sexo em falta **não** impediram a criação. Ficam utilizáveis para consulta, receção, faturação e laboratório. Confirmação clínica via aviso na ficha.

## Idempotência

Dry-run `--patients-only` após o apply ainda reporta 151 «a criar» + 5 «a associar» porque o plano de staging não desconta `migration_id` já na BD; 5 linhas passam a `SAFE_MATCH` **consigo próprias** (mesmo pk).

Verificação segura (`_existing_patient` por `migration_id`):

- 151 prontos já existentes
- 5 «associar» já existentes (self-match, sem merge)
- **0** novos a criar

Não foi executado um segundo `--apply` de pacientes (desnecessário e evitado). Duplicação não ocorre no caminho de apply.

## Decisão

Sem problema crítico. Prosseguir para `--history-only`.
