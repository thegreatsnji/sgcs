# Sprint 21 Fase 3 — Pré-verificação

**Data:** 2026-08-17  
**Batch:** `SAUVIDA-HIST-V1`  
**Resultado:** **APROVADO** — sem divergência de contagens. Apply autorizado neste ambiente.

## Ambiente

| Campo | Valor |
| --- | --- |
| Projecto | SGCS (Docker Compose local) |
| `APP_ENV` | `development` |
| `DEBUG` | `true` |
| Produção clínica | **Não** |
| Motor BD | PostgreSQL 16 (`django.db.backends.postgresql`) |
| Base de dados | `sgcs` |
| Host BD (contentor backend) | `db` |
| Host BD (Compose) | `sgcs-db` |
| Actor administrador | `admin@sauvida.gw` (activo, `Administrador`) |
| Batch id | `SAUVIDA-HIST-V1` |

Não é produção clínica. Não foi usada autorização de produção.

## Ficheiros privados

Pasta: `backend/data/private/sauvida_migration/` (gitignored: `.gitignore` linha `backend/data/private/`).

| Ficheiro | Presente |
| --- | --- |
| `sauvida_historico_original.xlsx` | sim |
| `pacientes_migracao_sauvida.csv` | sim |
| `historico_clinico_sauvida.csv` | sim |
| `historico_financeiro_sauvida.csv` | sim |
| `stock_referencia_sauvida.csv` | sim |
| CSVs de revisão / duplicados / órfãos / datas / stock | sim |

O Excel original **não** foi modificado.

## Contagens dry-run (`--skip-blocked`, batch `SAUVIDA-HIST-V1`)

| Indicador | Esperado | Observado | Estado |
| --- | --- | --- | --- |
| Pacientes prontos | 156 | 156 | OK |
| Pacientes bloqueados | 38 | 38 | OK |
| Correspondências seguras SGCS | 0 | 0 | OK |
| Eventos prontos | 182 | 182 | OK |
| Eventos bloqueados | 66 | 66 | OK |
| Eventos sem paciente (não importáveis) | 173 | 173 | OK |
| Itens stock candidatos | 55 | 55 | OK |
| Sobreposição prontos ∩ bloqueados (pacientes) | 0 | 0 | OK |
| Sobreposição prontos ∩ bloqueados (eventos) | 0 | 0 | OK |

Stock **não** entra no plano de importação (`STOCK_IN_PLAN_KEYS` vazio). `quantidade_inicial` permanece vazia. Fase 3 **não** importa stock.

## Contagens BD antes do apply

Patient 10 · PatientHistory 10 · User 12 · Appointment 8 · Fatura 5 · Pagamento 5 · Recibo 5 · PedidoLaboratorial 2 · MedicamentoUrgencia 9 · MovimentoStockUrgencia 0 · MovimentoFinanceiro 5.

Pacientes com `source=MIGRACAO_EXCEL_SAUVIDA`: 0.

## Backup

Ver `docs/MIGRACAO_HISTORICA_BACKUP.md` e `docs/logs/sprint21_fase3_backup.txt`.

Dump PostgreSQL real, tamanho > 0, SHA256 registado. Sem credenciais no log.
