# Backup — stock inicial

**Apply real:** não executado (0 itens VALIDOS na ficha).

Não foi gerado dump PostgreSQL específico desta operação porque **não houve escrita**.

Quando a enfermeira preencher `manter_no_stock=SIM`, unidade e `quantidade_actual` inteira:

1. `python manage.py backup_sauvida_pre_apply` (ou `pg_dump` via `sgcs-db`).
2. Confirmar tamanho > 0 e SHA256 no `.meta.txt`.
3. Só então `--apply --actor-email`.

Restore (exemplo, sem password):

```bash
docker exec -i sgcs-db psql -U sgcs sgcs < backups/pre_sauvida_hist/FICHEIRO.sql
```
