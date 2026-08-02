# Importação final — catálogo real

## Pré-apply

1. Validar `catalogo_servicos_sauvida_real.csv`.
2. Backup BD (`sprint18_backup_db` ou procedimento Docker).
3. Checksum do ficheiro.
4. Dry-run e comparar com **121** preços confirmados.
5. Confirmar **12** pendentes não importados como confirmados.
6. Confirmar **6** conflitos sem resolução automática.

## Comandos

```bash
python manage.py import_catalogo_sauvida \
  --file backend/data/catalogo_servicos_sauvida_real.csv \
  --dry-run \
  --update-existing \
  --actor-email EMAIL_ADMINISTRADOR
```

Log: `docs/logs/catalogo_real_dry_run_final.txt`

Apply (após validação clínica):

```bash
python manage.py import_catalogo_sauvida \
  --file backend/data/catalogo_servicos_sauvida_real.csv \
  --apply \
  --update-existing \
  --actor-email EMAIL_ADMINISTRADOR
```

Log: `docs/logs/catalogo_real_apply_final.txt`

**Estado actual:** apply não executado nesta entrega.
