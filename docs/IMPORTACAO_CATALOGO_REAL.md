# Importação do catálogo real (OCR)

## Pré-requisitos

1. Regenerar CSV: `python scripts/build_catalogo_real_from_ocr.py`
2. Backup: `python manage.py sprint18_backup_db` (ou `pg_dump` via Docker)
3. Revisar `docs/OCR_ANALISE_IMAGENS.md` e `docs/COMPARACAO_CATALOGO_PREPARADO_REAL.md`

## Dry-run (obrigatório)

```bash
cd backend
python manage.py import_catalogo_sauvida \
  --file data/catalogo_servicos_sauvida_real.csv \
  --dry-run \
  --create-missing-relations \
  --materialize-without-price \
  --update-existing
```

Log: `docs/logs/sprint18_catalogo_real_dry_run.txt`

## Apply

Só após dry-run sem erros críticos e backup validado:

```bash
python manage.py import_catalogo_sauvida \
  --file data/catalogo_servicos_sauvida_real.csv \
  --apply \
  --create-missing-relations \
  --materialize-without-price \
  --update-existing \
  --actor-email admin@sauvida.gw
```

## Exames laboratoriais

Após serviços na BD:

```bash
python manage.py import_catalogo_sauvida \
  --file data/catalogo_servicos_sauvida_real.csv \
  --exames data/exames_laboratoriais_reais.csv \
  --apply --update-existing

python manage.py align_lab_services --dry-run
python manage.py align_lab_services --apply
```

## Comportamento

- Linhas com `preco_confirmado=FALSE` materializam com preço 0 e bloqueio de faturação (Sprint 17).
- `operacional=0` desactiva na receção.
- Histórico e auditoria em alterações de preço confirmado.

## Substituição do catálogo preparado

O ficheiro `catalogo_servicos_sauvida.csv` (36 itens, preços pendentes) **mantém-se** como referência histórica.  
O catálogo operacional passa a ser `catalogo_servicos_sauvida_real.csv` após `--apply`.
