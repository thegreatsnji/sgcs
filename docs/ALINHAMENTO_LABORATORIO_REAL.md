# Alinhamento laboratório — catálogo real

Ficheiro: `backend/data/exames_laboratoriais_reais.csv` (~97 exames).

```bash
python manage.py align_lab_services \
  --file backend/data/exames_laboratoriais_reais.csv \
  --dry-run
```

Log: `docs/logs/lab_real_alignment_dry_run.txt`

```bash
python manage.py align_lab_services \
  --file backend/data/exames_laboratoriais_reais.csv \
  --apply
```

Log: `docs/logs/lab_real_alignment_apply.txt`

Exames ambíguos ou sem `servico_codigo` não são forçados. O comando suporta `--file` como alias de `--exames`.
