# Backup obrigatório antes de `--apply`

Nenhum `--apply` da migração histórica sem dump PostgreSQL válido.

## Comando Django

```bash
python manage.py backup_sauvida_pre_apply
```

Opções: `--output-dir` (pasta de destino). Confirmado via `--help`.

No contentor `sgcs-backend` este comando **falha**: não existe `docker` nem `pg_dump` na imagem. Equivalente usado na Fase 3 (host Windows + Docker):

```bash
docker exec sgcs-db pg_dump -U sgcs --no-owner --no-acl -f /tmp/sgcs_pre_sauvida_hist_TIMESTAMP.sql sgcs
docker cp sgcs-db:/tmp/sgcs_pre_sauvida_hist_TIMESTAMP.sql backups/pre_sauvida_hist/
```

O dump **não** inclui password na linha de comando. Pasta `backups/` está no `.gitignore`.

## Backup Fase 3 (2026-08-17)

| Campo | Valor |
| --- | --- |
| Ambiente | `development` (Docker Compose local, **não** produção) |
| Base de dados | `sgcs` em `sgcs-db` (PostgreSQL 16.14) |
| Ficheiro | `backups/pre_sauvida_hist/sgcs_pre_sauvida_hist_20260817_152144.sql` |
| Tamanho | 499108 bytes |
| SHA256 | `6c8fdb901bb373b2f602dda359b1dd0abedd279aedde3a548914e87879daebc0` |
| Cabeçalho | `-- PostgreSQL database dump` |
| Meta | `backups/pre_sauvida_hist/sgcs_pre_sauvida_hist_20260817_152144.meta.txt` |
| Log | `docs/logs/sprint21_fase3_backup.txt` |

## Validar o backup

1. Ficheiro existe e tamanho > 0.
2. SHA256 no `.meta.txt` coincide com `Get-FileHash -Algorithm SHA256`.
3. Cabeçalho PostgreSQL presente.
4. Só então: `--apply --confirm-backup`.

## Restauro

O restauro **substitui** o estado da BD `sgcs`. Não executar sobre movimento clínico posterior à importação sem plano de reconciliação.

A partir do host (PowerShell), exemplo:

```powershell
Get-Content backups\pre_sauvida_hist\sgcs_pre_sauvida_hist_20260817_152144.sql -Raw |
  docker exec -i sgcs-db psql -U sgcs sgcs
```

Em bash:

```bash
docker exec -i sgcs-db psql -U sgcs sgcs < backups/pre_sauvida_hist/sgcs_pre_sauvida_hist_20260817_152144.sql
```

Confirmar SHA256 antes de restaurar:

```powershell
Get-FileHash -Algorithm SHA256 backups\pre_sauvida_hist\sgcs_pre_sauvida_hist_20260817_152144.sql
```

Esperado: `6c8fdb901bb373b2f602dda359b1dd0abedd279aedde3a548914e87879daebc0`.
