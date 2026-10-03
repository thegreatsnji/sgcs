# Sprint 21 Fase 4 — Auditoria do batch `SAUVIDA-HIST-V1`

**Data:** 2026-08-17  
**Ambiente:** development (Docker Compose local)  
**Fonte:** `MIGRACAO_EXCEL_SAUVIDA`  
**Escrita na BD:** não  
Apenas agregados. Sem dados identificáveis.

Comando:

```bash
python manage.py audit_sauvida_history_batch --batch-id SAUVIDA-HIST-V1
```

## Tabela agregada

| Modelo / tipo | Quantidade |
| ------------- | ---------: |
| Patient (batch) | 156 |
| PatientHistory total do lote | 338 |
| PatientHistory REGISTO (auxiliar de importação do utente) | 156 |
| PatientHistory clínicos | 182 |
| PatientHistory financeiro extra (`KIND`) | 0 |
| AuditLog com `import_batch` | 156 |
| Evento clínico CONSULTA | 111 |
| Evento clínico CONTROLO | 16 |
| Evento clínico LABORATORIO | 43 |
| Evento clínico ECOGRAFIA | 8 |
| Evento clínico CIRURGIA | 4 |
| Eventos órfãos | 0 |
| `migration_id` duplicados | 0 |
| Provenance incompleta (pacientes) | 0 |
| Provenance incompleta (histórico clínico) | 0 |
| Históricos em pacientes externos ao lote | 0 |

## Folhas de origem (eventos clínicos)

CONSULTAS_CONTROLOS 91 · CONSULTAS ADULTOS AGOSTO 22 · LABORATORIO 31 · CONSULTAS PED 10 · ANALISES 12 · ECOGRAFIA 6 · CONTROLOS 4 · CIRUGIA 3 · ECOGRAFIA AGOSTO 2 · CIRURGIA AGOSTO 1.

## Objectos auxiliares

Cada um dos 156 pacientes recebeu um `PatientHistory` de tipo `REGISTO` («Utente importado do registo anterior da clínica»). Isto **não** é um acto clínico extraído do Excel. Explica a diferença 182 vs 338. Ver `docs/SPRINT21_FASE4_ROLLBACK_RECONCILIATION.md`.

156 `AuditLog` `PATIENT_CREATE` com o mesmo `import_batch` — trilha forense, **não** incluída no rollback.

## Leakage

Financeiro (Fatura/Pagamento/Recibo/MovimentoFinanceiro/Appointment/PedidoLaboratorial com o batch): **0**.  
Stock (MedicamentoUrgencia / MovimentoStockUrgencia): **0**.  
Tabelas inesperadas: nenhuma.
