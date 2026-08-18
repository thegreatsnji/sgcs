# Migração histórica SauVida — Sprint 21 Fase 2

**Estado:** pipeline de importação implementado. **`--apply` não foi executado.**  
**Lote previsto:** `SAUVIDA-HIST-V1`

## O que mudou

- A revisão deixou de ser “739 itens = bloqueio total”.
- Pacientes incompletos (sem telefone, morada, nascimento ou sexo) **podem** ser importados como `IMPORTADO_NAO_VERIFICADO`.
- Duplicados, datas suspeitas e laboratório `AMBIGUO` continuam **bloqueantes**.
- Eventos sem paciente **não** geram utentes fictícios.
- Histórico clínico vai para `PatientHistory` (não cria consultas/faturas/resultados modernos).
- Stock actual **não** é criado; a enfermeira confirma numa lista privada.

## Fluxo

```bash
python backend/scripts/prioritize_sauvida_historical_review.py
python manage.py backup_sauvida_pre_apply
python manage.py import_sauvida_history --dry-run --skip-blocked --batch-id SAUVIDA-HIST-V1
# Só após autorização explícita:
python manage.py import_sauvida_history --apply --patients-only --skip-blocked --confirm-backup --batch-id SAUVIDA-HIST-V1 --actor-email EMAIL
python manage.py import_sauvida_history --apply --history-only --skip-blocked --confirm-backup --batch-id SAUVIDA-HIST-V1 --actor-email EMAIL
```

Rollback:

```bash
python manage.py rollback_sauvida_history --batch-id SAUVIDA-HIST-V1 --dry-run
python manage.py rollback_sauvida_history --batch-id SAUVIDA-HIST-V1 --apply
```

## Proveniência

Cada objecto importado guarda `source=MIGRACAO_EXCEL_SAUVIDA`, `import_batch`, `migration_id` / `historico_id`, folha, linha, `imported_at`, `imported_by`.  
`record_class=HISTORICO_IMPORTADO` (distinto de `OPERACAO_SGCS`).

## Documentos

- [Priorização da revisão](MIGRACAO_HISTORICA_PRIORIZACAO_REVISAO.md)
- [Backup](MIGRACAO_HISTORICA_BACKUP.md)
- [Dry-run](MIGRACAO_HISTORICA_DRY_RUN.md)
- [Pós-importação](MIGRACAO_HISTORICA_POS_IMPORTACAO.md)
- [Relatório Fase 2](SPRINT21_FASE2_REPORT.md)
