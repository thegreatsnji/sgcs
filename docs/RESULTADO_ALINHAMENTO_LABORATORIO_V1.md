# Resultado alinhamento laboratório V1

Dry-run:

```bash
python manage.py align_lab_services \
  --file backend/data/releases/exames_laboratoriais_sauvida_v1.csv \
  --dry-run
```

Log: `docs/logs/exames_sauvida_v1_alignment_dry_run.txt`

Apply (após aprovação):

```bash
python manage.py align_lab_services \
  --file backend/data/releases/exames_laboratoriais_sauvida_v1.csv \
  --apply
```

Log: `docs/logs/exames_sauvida_v1_alignment_apply.txt`

**Estado:** apply pendente.
