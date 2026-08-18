# Sprint 21 Fase 5 — Relatório

**Data:** 2026-08-17  
**Ambiente:** development (Docker Compose local)  
**Apply / rollback real:** **não executados**  
**Estado:** `AGUARDA_VALIDACAO_CLINICA`

## 1. Ficheiros de validação

Pacote privado (gitignored) em `backend/data/private/sauvida_migration/validation_pack/`:

| Ficheiro | Destinatário |
| --- | --- |
| `pacientes_duplicados_validacao.xlsx` | Receção / direcção |
| `eventos_bloqueados_validacao.xlsx` | Coordenação clínica |
| `laboratorio_historico_validacao.xlsx` | Técnico de laboratório |
| `medicos_historicos_validacao.xlsx` | Direcção |
| `stock_urgencia_validacao.xlsx` | Enfermeira |
| `datas_suspeitas_validacao.xlsx` | Coordenação clínica |

Decisões: `MESMA_PESSOA` / `PESSOAS_DIFERENTES` / `INDETERMINADO` (sem merge). `MANTER_TEXTUAL` é válido. Datas nunca se corrigem sozinhas.

## 2. Pendências (agregados)

| Item | Quantidade |
| --- | ---: |
| Pares duplicados | 23 |
| Pacientes bloqueados | 38 |
| Eventos bloqueados | 66 |
| Labs ambíguos (eventos / descrições) | 13 / 2 |
| Datas problemáticas | 5 (4 eventos + 1 sem data) |
| Médicos não mapeados | 3 |
| Stock a validar (não importar) | 55 |

Eventos bloqueados (causa primária): 48 `PACIENTE_DUPLICADO`, 13 `LAB_AMBIGUO`, 4 `DATA_SUSPEITA`, 1 `SEM_DATA`.

## 3. Batch de revisão

`SAUVIDA-HIST-V1-REVIEW` é **distinto** de `SAUVIDA-HIST-V1`.  
`--reviewed-only --batch-id SAUVIDA-HIST-V1` é recusado.

Dry-run actual (sem decisões clínicas): **0 a importar**. Correcto.

Relatório esperado após preenchimento: pacientes desbloqueados, merges `MESMA_PESSOA` (alias, sem apagar), pacientes separados, eventos desbloqueados, labs mapeados, labs textuais, datas corrigidas pela clínica, médicos mapeados, ainda bloqueados.

## 4. Merge

Canónico = menor `migration_id`. Alias em metadata + linha `PatientHistory`. Histórico e provenance **não** são apagados. `INDETERMINADO` = não fundir.

## 5. Runbook e piloto

- `docs/RUNBOOK_MIGRACAO_HISTORICA_PRODUCAO.md`
- `docs/MIGRACAO_HISTORICA_PILOT_CHECKLIST.md`

## 6. Testes e gates

- `manage.py check`: OK  
- `makemigrations --check`: OK  
- `apps/data_migration/tests/`: **52 passed**, 2 skipped (lab ambíguo ausente no workbook sintético)  
- Suite completa: **371 passed**, 2 skipped, **2 failed** pré-existentes na Receção (médico indisponível; fora de âmbito)

Dry-run `SAUVIDA-HIST-V1-REVIEW` sem decisões: 0 pacientes / 0 eventos a importar; 38+66 ainda bloqueados. BD do lote inicial inalterada (156 Patient, 338 PatientHistory).

## 7. Readiness produção

Código e runbook prontos para **repetir** o lote inicial no piloto **depois** da validação clínica do pacote.  
**Não** está autorizado apply nesta fase.

**AGUARDA_VALIDACAO_CLINICA**
