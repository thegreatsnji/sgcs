# Backup pré Catálogo SauVida V1

## Comando

```bash
python manage.py backup_pre_catalogo_sauvida_v1
```

## Destino

`backups/pre_catalogo_sauvida_v1/sgcs_pre_catalogo_sauvida_v1_YYYYMMDD_HHMM.sql`  
Ficheiro `.sha256` com checksum.

## Pré-requisitos

- `pg_dump` no PATH (ou executar dentro do contentor PostgreSQL).
- Credenciais via `DATABASES` (não guardar passwords no repositório).

## Restauração (teste)

```bash
psql -h HOST -U USER -d DATABASE -f backups/pre_catalogo_sauvida_v1/<ficheiro>.sql
```

## Registo de execução (2026-08-02 — apply operacional)

| Campo | Valor |
|---|---|
| Ambiente | Dev local (`APP_ENV=development`, `sgcs` @ `localhost`, contentor `sgcs-db`) |
| Ficheiro | `backups/pre_catalogo_sauvida_v1/sgcs_pre_catalogo_sauvida_v1_20260802_1537.sql` |
| Tamanho | 438537 bytes |
| SHA256 | `e9f3e6c7c9f20fe53b81ad7484f4c75ff932c1dd32174a30f800780c2d9c3f73` |
| Método | `docker exec sgcs-db pg_dump` (pg_dump ausente no host Windows) |
| Log | `docs/logs/backup_pre_catalogo_sauvida_v1.txt` |
| Actor previsto (import) | `admin@sauvida.ao` |

## Registo anterior (2026-07-31)

| Campo | Valor |
|---|---|
| Ficheiro | `backups/pre_catalogo_sauvida_v1/sgcs_pre_catalogo_sauvida_v1_20260731_1555.sql` |
| Tamanho | 384704 bytes |
| SHA256 | `7069561488410c6c26a7805418ecd87323036b599bb02d1b5f6439556d0c3f81` |

**Não executar apply do catálogo V1 se o backup falhar.**
