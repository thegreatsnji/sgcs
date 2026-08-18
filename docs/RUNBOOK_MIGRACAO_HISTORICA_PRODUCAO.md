# Runbook — migração histórica SauVida (piloto / produção)

**Âmbito:** repetir a importação segura do lote inicial.  
**Não incluir passwords neste documento.**  
Excel e CSVs privados **nunca** vão para o Git.

## Contagens aprovadas (lote inicial)

| Métrica | Valor |
| --- | ---: |
| Pacientes a criar (`--skip-blocked`) | 156 |
| Pacientes bloqueados | 38 |
| Eventos clínicos a criar | 182 |
| Eventos bloqueados | 66 |
| Eventos sem paciente (não importar) | 173 |
| Stock | não importar |

SHA256 do Excel original (inalterado):

`bfd987eec4a82c454d1a4519d460ef64fcad16b91dcb47af95fe6a6847ce6822`

Lote inicial: `SAUVIDA-HIST-V1`  
Lote de revisões posteriores: `SAUVIDA-HIST-V1-REVIEW` (**nunca** reaplicar o lote inicial para desbloquear).

Actor: um `Administrador` **já existente** (`--actor-email`).

## Batches

| Batch | Quando | Conteúdo |
| --- | --- | --- |
| `SAUVIDA-HIST-V1` | Primeira importação segura | 156 pacientes + 182 eventos (`--skip-blocked`) |
| `SAUVIDA-HIST-V1-REVIEW` | Só após Excel de validação preenchidos | Itens desbloqueados por decisão clínica |

Nunca reaplicar `SAUVIDA-HIST-V1` para resolver bloqueados.

## Sequência (lote inicial)

### 1. Ficheiros privados

Confirmar em `backend/data/private/sauvida_migration/`:

- `sauvida_historico_original.xlsx`
- `pacientes_migracao_sauvida.csv`
- `historico_clinico_sauvida.csv`
- CSVs/Excel de revisão (duplicados, eventos bloqueados, lab, médicos, stock)

A pasta está no `.gitignore` (`backend/data/private/`).

### 2. SHA256 do Excel

```powershell
Get-FileHash -Algorithm SHA256 backend\data\private\sauvida_migration\sauvida_historico_original.xlsx
```

**PARAR** se o hash divergir.

### 3. Versão do código

Confirmar que o deploy inclui `apps.data_migration`, os comandos `import_sauvida_history`, `backup_sauvida_pre_apply`, `rollback_sauvida_history`, `audit_sauvida_history_batch`, e a migration `patients.0002_sprint21_fase2_historical_import`.

```bash
git log -1 --oneline
```

### 4. Migrations

```bash
python manage.py makemigrations --check
python manage.py migrate
python manage.py check
```

### 5. Backup PostgreSQL

No contentor backend o `manage.py backup_sauvida_pre_apply` pode falhar (sem `pg_dump`/`docker`). Equivalente:

```bash
docker exec sgcs-db pg_dump -U sgcs --no-owner --no-acl -f /tmp/sgcs_pre_sauvida_hist_TIMESTAMP.sql sgcs
docker cp sgcs-db:/tmp/sgcs_pre_sauvida_hist_TIMESTAMP.sql backups/pre_sauvida_hist/
```

Validar: ficheiro existe, tamanho > 0, SHA256 no `.meta.txt`, cabeçalho `PostgreSQL database dump`. Sem password na linha de comando.

### 6. Validar o backup

```powershell
Get-FileHash -Algorithm SHA256 backups\pre_sauvida_hist\FICHEIRO.sql
```

Teste de restore **só** num clone da BD (nunca por cima de movimento clínico posterior sem plano):

```bash
# Apenas num clone da BD. Substitui o conteúdo de `sgcs`.
docker exec -i sgcs-db psql -U sgcs sgcs < backups/pre_sauvida_hist/FICHEIRO.sql
```

Validar SHA256 do dump antes de restaurar.

### 7. Dry-run

```bash
python manage.py import_sauvida_history --dry-run --skip-blocked --batch-id SAUVIDA-HIST-V1
```

### 8. Comparar contagens

Exigir exactamente 156 pacientes prontos, 38 bloqueados, 182 eventos prontos, 66 bloqueados, 173 órfãos, stock não processado. **PARAR** se divergir.

### 9. Apply patients-only

```bash
python manage.py import_sauvida_history --apply --patients-only --skip-blocked --batch-id SAUVIDA-HIST-V1 --actor-email EMAIL_ADMIN --confirm-backup
```

### 10. Auditoria de pacientes

```bash
python manage.py audit_sauvida_history_batch --batch-id SAUVIDA-HIST-V1
```

Esperado: 156 Patient, 156 PatientHistory `REGISTO`, 0 órfãos, 0 leakage.

### 11. Apply history-only

```bash
python manage.py import_sauvida_history --apply --history-only --skip-blocked --batch-id SAUVIDA-HIST-V1 --actor-email EMAIL_ADMIN --confirm-backup
```

### 12. Auditoria de histórico

O mesmo `audit_sauvida_history_batch`. Esperado: 182 clínicos, 338 PatientHistory no lote (156+182), 0 faturas/pagamentos/recibos/stock novos.

### 13. Rollback dry-run (não aplicar)

```bash
python manage.py rollback_sauvida_history --batch-id SAUVIDA-HIST-V1 --dry-run
```

Esperado: 156 pacientes, 338 históricos, `historicos_clinicos=182`, `historicos_registo_importacao=156`, `historicos_em_pacientes_externos=0`. **PARAR** se houver objectos fora do lote.

### 14. Smoke test

Abrir um utente importado: aviso «Dados provenientes do registo anterior da clínica…», acção «Confirmar dados». Receção consegue editar telefone/residência/nascimento/sexo. Consulta, faturação e laboratório **não** bloqueiam por campos em falta.

### 15. Validação por Receção

Confirmar dados na ficha (não apaga provenance). Não fundir duplicados.

### 16. Relatórios

Guardar logs em `docs/logs/` (sem PII) e o output de `audit_sauvida_history_batch --json`.

### 17. Monitorizar

Caixa, faturas do dia e stock de urgência devem permanecer iguais às contagens pré-importação. Qualquer factura/pagamento/recibo novo **não** deve ter origem `MIGRACAO_EXCEL_SAUVIDA`.

### 18. Smoke na interface

Receção: pesquisar utente importado → aviso → actualizar telefone → confirmar dados.  
Médico: histórico importado visível e distinto de consulta nova.  
Director: receita/caixa/dívida iguais ao pré-import.  
Laboratório: texto histórico visível, sem resultado estruturado inventado.

## Lote de revisão (`SAUVIDA-HIST-V1-REVIEW`)

Só depois dos Excel em `validation_pack/` preenchidos:

```bash
python manage.py prepare_sauvida_review_packs
python manage.py import_sauvida_history --dry-run --reviewed-only --skip-blocked --batch-id SAUVIDA-HIST-V1-REVIEW
```

Conferir: pacientes desbloqueados, merges `MESMA_PESSOA` (alias), pacientes separados, eventos desbloqueados, labs mapeados, labs textuais, datas corrigidas, médicos mapeados, ainda bloqueados.

`--reviewed-only --batch-id SAUVIDA-HIST-V1` é **recusado**.  
Apply do REVIEW só com backup novo e autorização explícita (não nesta fase).

`INDETERMINADO` = não fundir. Canónico = menor `migration_id`. Histórico não se apaga.

## Stop conditions (piloto/produção)

Parar imediatamente se:

- checksum do Excel divergir;
- staging/dry-run divergir de 156 / 182;
- backup inválido ou vazio;
- dry-run apontar faturas, pagamentos ou stock;
- paciente ou evento bloqueado for importado;
- rollback dry-run listar objectos fora do batch (`historicos_em_pacientes_externos > 0`);
- provenance ausente;
- existirem eventos órfãos;
- segunda execução criar duplicados técnicos.
