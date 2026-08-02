# Sprint 18.2 — Implantação operacional Catálogo SauVida V1

**Data do apply:** 2026-08-02  
**Ambiente:** desenvolvimento local (`APP_ENV=development`, PostgreSQL `sgcs` @ `localhost`, contentor `sgcs-db`) — **não é produção clínica.**

## 1. Ambiente e pré-verificação

| Item | Valor |
|---|---|
| Actor auditoria (Administrador) | `admin@sauvida.ao` |
| Ficheiro catálogo | `backend/data/releases/catalogo_sauvida_v1.csv` |
| Ficheiro exames | `backend/data/releases/exames_laboratoriais_sauvida_v1.csv` |
| SHA-256 catálogo | `32cc9123087de039c0bef965aa61cdee4cd63d50295a32278711fe698000104f` |
| SHA-256 exames | `c5e35bd97b3352705f9a1132094691ec51a4dcb3f08f94d0ee08d0a3bbeb6678` |
| Linhas importáveis | 119 |
| Pendentes / duplicados / preços negativos | 0 |
| Moeda | FCFA (pré-flight CSV) |

Log: `docs/logs/preflight_catalogo_v1.txt`

## 2. Backup

| Campo | Valor |
|---|---|
| Criado | **SIM** |
| Caminho | `backups/pre_catalogo_sauvida_v1/sgcs_pre_catalogo_sauvida_v1_20260802_1537.sql` |
| Tamanho | 438537 bytes |
| SHA-256 | `e9f3e6c7c9f20fe53b81ad7484f4c75ff932c1dd32174a30f800780c2d9c3f73` |
| Método | `docker exec sgcs-db pg_dump` (`manage.py backup_pre_catalogo_sauvida_v1` indisponível no host: sem `pg_dump`) |

Documentação: `docs/BACKUP_CATALOGO_SAUVIDA_V1.md`, `docs/logs/backup_pre_catalogo_sauvida_v1.txt`

## 3. Apply do catálogo V1

Comando:

```bash
python manage.py import_catalogo_sauvida \
  --file data/releases/catalogo_sauvida_v1.csv \
  --exames data/releases/exames_laboratoriais_sauvida_v1.csv \
  --apply --update-existing \
  --actor-email admin@sauvida.ao
```

| Métrica | Valor |
|---|---:|
| Criados | 0 |
| Actualizados | **119** |
| Pendentes revisão | 0 |
| Ignorados | 0 |
| Erros | 0 |

**Nota:** na BD de desenvolvimento os 119 códigos V1 já existiam (import anterior); o apply foi **idempotente** (actualização, não inserção). Em BD vazia o resultado esperado é 119 criados.

Log: `docs/logs/catalogo_sauvida_v1_apply.txt`

## 4. Validação pós-importação

Documento: `docs/VALIDACAO_POS_IMPORTACAO_CATALOGO_V1.md`

- 119 serviços `SAUVIDA_V1`, activos, preço confirmado, 0 arquivados V1
- 119 eventos `CATALOGO_REAL_IMPORTADO`
- Preservação de `ItemFatura` (snapshots; sem recálculo de recibos)

## 5. Arquivo catálogo legado

| Passo | Resultado |
|---|---|
| Dry-run | 1 serviço com `versao_catalogo != SAUVIDA_V1` |
| Apply | **1** arquivado (`LEGACY_PREPARED`) |

**Nota:** o pacote preparado de ~36 itens não estava materializado como serviços separados nesta BD; apenas 1 registo legado residual. Comportamento do comando correcto.

Logs: `docs/logs/archive_legacy_catalog_dry_run.txt`, `docs/logs/archive_legacy_catalog_apply.txt`

## 6. Alinhamento laboratorial

| Métrica | Valor |
|---|---:|
| Exames no CSV V1 | 87 |
| Alinhados (BD, pós-import) | **87** |
| Sem correspondência | **0** |
| Ambíguos | **0** |
| `align_lab_services` apply | 0 novos (já ligados via `_import_exames` no import) |

Documento: `docs/VALIDACAO_ALINHAMENTO_LAB_V1.md`  
Logs: `docs/logs/exames_sauvida_v1_alignment_dry_run_pos_import.txt`, `exames_sauvida_v1_alignment_apply.txt`

## 7. Smoke / fluxo financeiro / recibo

| Área | Evidência |
|---|---|
| Catálogo operacional (API) | `test_sprint18_2_catalog_v1` — `operacional=1`, legado oculto |
| Redução (casos B, D) | `test_sprint18_1_reductions.py` |
| Pagamento parcial (caso C) | `test_sprint18_2` `TestPagamentoParcialSaldo` |
| Preservação fatura (caso A histórico) | `test_sprint18.py` |
| Recibo ORIGINAL / contexto SauVida | `test_sprint18_2` `TestReciboImpressao` |

Subconjunto billing: **22 passed** — `docs/logs/sprint18_2_smoke_billing.txt`  
Nota UAT UI: `docs/logs/sprint18_2_uat_api_smoke.txt`

## 8. Gates finais

| Gate | Resultado | Log |
|---|---|---|
| `manage.py check` | OK | `docs/logs/sprint18_2_manage_check_final.txt` |
| `makemigrations --check` | OK (sem alterações) | `docs/logs/sprint18_2_migrations_final.txt` |
| `pytest -q --reuse-db` | **305 passed** | `docs/logs/sprint18_2_pytest_final.txt` |
| `npm run build` | OK (exit 0) | `docs/logs/sprint18_2_build_final.txt` |
| `npm run lint` | **0 erros** (8 avisos) | `docs/logs/sprint18_2_lint_final.txt` |

## 9. Problemas e correcções

| Problema | Acção |
|---|---|
| `pg_dump` ausente no Windows | Backup via Docker `sgcs-db` |
| Apply reportou 0 criados / 119 actualizados | Esperado em BD já importada; validação confirma 119 V1 |
| Smoke shell com APIClient | DisallowedHost; coberto por pytest |
| Apenas 1 legado arquivado | Estado real da BD dev, não falha do arquivo |

## 10. Estado da implantação e piloto

| Critério | Estado |
|---|---|
| Backup válido | **APROVADO** |
| Catálogo V1 na BD | **APROVADO** (119) |
| Validação pós-importação | **APROVADO** |
| Legado arquivado | **APROVADO** (1 registo) |
| Laboratório alinhado | **APROVADO** (87/87, 0 ambíguos) |
| Gates automatizados | **APROVADO** |
| Conflitos clínica / manuscritos | **PENDENTE** (`DECISOES_CATALOGO`, validação manuscrita) |
| UAT Receção presencial | **PENDENTE** |

**Implantação técnica (dev):** concluída com sucesso.  
**Piloto clínico:** pronto para **UAT na Receção** após repetir backup+apply no ambiente piloto da clínica e assinatura dos itens pendentes de negócio.

## Próximos passos estritamente necessários

1. Repetir sequência backup → apply → archive → lab no ambiente piloto (não dev).
2. Executar UAT (`docs/SPRINT18_UAT_RECECAO.md` / pacote piloto) com rececionista real.
3. Resolver conflitos `PENDENTE_CLINICA` antes de produção.
4. Instalar `pg_dump` no host ou documentar backup Docker no runbook da clínica.
