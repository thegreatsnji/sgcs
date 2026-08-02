# Sprint 18 — Backup e restauro (pré-importação)

## Motor

PostgreSQL 16 (desenvolvimento local via Docker `sgcs-db`).

## Backup Sprint 18 (executado)

| Campo | Valor |
|-------|--------|
| Ficheiro | `backups/pre_sprint18/sgcs_pre_import_catalogo_20260731_1400.sql` |
| SHA256 | `3710D12026F444A9ED9E68FB758A7B998EA69074A70F3B2BAC9064C235A30089` |
| Método | `docker exec sgcs-db pg_dump -U sgcs sgcs` |

Meta: ficheiro `.meta.txt` junto ao dump.

## Comando de backup

```bash
cd backend
python manage.py sprint18_backup_db
```

Ficheiros gerados em `backups/pre_sprint18/`:

- `sgcs_pre_import_catalogo_YYYYMMDD_HHMM.sql`
- `sgcs_pre_import_catalogo_YYYYMMDD_HHMM.meta.txt` (tamanho e SHA256)

**Não incluir credenciais** neste documento; usar variáveis de ambiente (`DB_*`, `PGPASSWORD` apenas na sessão).

## Restauro

```bash
psql -h HOST -p PORT -U USER -d DATABASE -f backups/pre_sprint18/sgcs_pre_import_catalogo_YYYYMMDD_HHMM.sql
```

## Validar restauro

1. `python manage.py check`
2. Contagem de serviços: `python manage.py shell -c "from apps.billing.models import Servico; print(Servico.objects.count())"`
3. Login na aplicação e listagem de faturação.

## Limitações

- O backup via API `settings/backups` permanece em modo estrutural (tarefa Celery stub).
- Sem `pg_dump` no PATH, usar dump manual do contentor: `docker exec sgcs-db pg_dump -U sgcs sgcs > backups/pre_sprint18/manual.sql`
- Restauro sobrescreve dados — executar apenas em ambiente de piloto controlado.

## Política Sprint 18

**Não executar `--apply` de importação de preços se o backup falhar ou estiver vazio.**
