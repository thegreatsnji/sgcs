# Rollback da migração histórica SauVida

## Fase 1 (actual)

Não há dados históricos na BD operacional. Rollback = apagar CSVs privados e relatórios gerados, **sem** tocar no Excel original.

```text
backend/data/private/sauvida_migration/
```

O original permanece intacto fora do Git.

## Fase 2

`--apply` cria objectos com `metadata.import_batch`. Rollback:

```bash
python manage.py rollback_sauvida_history --batch-id SAUVIDA-HIST-V1 --dry-run
python manage.py rollback_sauvida_history --batch-id SAUVIDA-HIST-V1 --apply
```

Remove apenas `PatientHistory` e pacientes daquele lote, e só se não tiverem dependências operacionais SGCS.


## Backups

Antes de qualquer `--apply` futuro: backup PostgreSQL completo + cópia dos CSVs de staging aprovados.

Não restaurar backups por cima de movimentos clínicos posteriores à importação sem plano de reconciliação.
