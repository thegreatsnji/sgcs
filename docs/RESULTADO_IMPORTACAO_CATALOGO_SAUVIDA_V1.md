# Resultado importação Catálogo SauVida V1

**Estado:** APPLY **não executado** nesta entrega (aguarda assinatura clínica + backup).

## Dry-run

Log: `docs/logs/catalogo_sauvida_v1_dry_run.txt` (executar após backup):

```bash
python manage.py import_catalogo_sauvida \
  --file backend/data/releases/catalogo_sauvida_v1.csv \
  --dry-run --update-existing \
  --actor-email EMAIL_ADMINISTRADOR
```

## Apply (quando aprovado)

```bash
python manage.py archive_legacy_catalog
python manage.py import_catalogo_sauvida \
  --file backend/data/releases/catalogo_sauvida_v1.csv \
  --apply --update-existing \
  --actor-email EMAIL_ADMINISTRADOR
```

Log: `docs/logs/catalogo_sauvida_v1_apply.txt`

Pós-apply: `versao_catalogo=SAUVIDA_V1`, pendentes OCR não importados como confirmados.
