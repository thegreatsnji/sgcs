# Sprint 21 Fase 4 — Integridade do histórico clínico

**Lote:** `SAUVIDA-HIST-V1`  
**N eventos clínicos:** 182  
Eventos órfãos: **0**.

| Verificação | Resultado |
| --- | ---: |
| Paciente existente e não apagado | 182 / 182 |
| `migration_id` do evento = `migration_id` do utente | 182 / 182 |
| `historico_id` único | 182 (0 duplicados, 0 vazios) |
| `source_sheet` e `source_row` | 182 / 182 |
| `source=MIGRACAO_EXCEL_SAUVIDA` | 182 |
| `import_batch=SAUVIDA-HIST-V1` | 182 |
| `imported_by=admin@sauvida.gw` | 182 |
| `imported_at` presente | 182 |
| Descrição ou título original | 182 |
| `medico_sgcs` nulo | 182 |
| `medico_original` preenchido | 4 |
| Preço/desconto/líquido preservados (quando existiam) | 182 |
| Provenance incompleta | 0 |
| Eventos bloqueados importados | 0 |
| Eventos sem paciente importados | 0 |

## Distribuição

111 consultas · 16 controlos · 4 laboratório estruturado · 39 laboratório textual · 8 ecografias · 4 cirurgias.

Datas: as 4 datas suspeitas permanecem fora do lote. Os 182 importados têm `event_date` preenchida.
