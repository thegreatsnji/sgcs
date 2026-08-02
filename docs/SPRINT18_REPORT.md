# Relatório Sprint 18 — Passagem controlada para piloto

## 1. Resumo executivo

A Sprint 18 implementou **validação técnica** do ficheiro de preços, **backup** pré-importação, **dry-run** obrigatório, comandos de auditoria, testes de preservação de faturas e documentação UAT/piloto. **Nenhum preço foi inventado nem importado**: as 36 linhas permanecem **PENDENTES** até a clínica preencher `preco_confirmado_fcfa`. A materialização e o alinhamento laboratorial em `--apply` ficam **pendentes de execução operacional** após aprovação (scripts documentados).

**Decisão do piloto:** **APROVADO COM RESSALVAS** (bloqueio apenas na confirmação de preços e apply de catálogo/lab em produção).

## 2. Estado inicial

- 36 serviços no CSV de validação, 0 preços confirmados.
- Serviços na BD: predominantemente ausentes (relatório materialização).

## 3–6. Validação de preços

| Métrica | Valor |
|--------|------:|
| Linhas analisadas | 36 |
| Válidas | 0 |
| Pendentes | 36 |
| Inválidas | 0 |
| Duplicadas | 0 |

Relatório: `docs/SPRINT18_VALIDACAO_PRECOS.md`. Ficheiro original preservado; **sem** `precos_validacao_clinica_revisao.csv` (nada a corrigir).

## 7. Backup

`backups/pre_sprint18/sgcs_pre_import_catalogo_20260731_1400.sql` — ver `docs/SPRINT18_BACKUP_RESTORE.md`.

## 8. Dry-run

`docs/logs/sprint18_catalogo_dry_run.txt` — 0 confirmados, 36 pendentes. **Sem conflitos críticos.**

## 9–11. Materialização e preços

- **Criados/actualizados (apply):** 0 (apply não executado nesta entrega automatizada).
- **Preços importados:** 0.
- Dry-run materialização: `docs/logs/sprint18_materialize_dry_run.txt`.

## 12. Histórico de preços

Teste `test_sprint18.TestPreservacaoFatura` — alteração de catálogo não altera `ItemFatura.preco`.

## 13. Laboratório

Plano em `docs/SPRINT18_LAB_ALIGNMENT_RESULT.md`; apply após serviços na BD.

## 14–15. Médicos

`docs/SPRINT18_MEDICOS_CONFIGURACAO.md` — perfis demo tipicamente **PENDENTE_DE_CONFIGURACAO** até sessão admin.

## 16–17. UAT

`docs/SPRINT18_UAT_RECECAO.md`, `docs/SPRINT18_UAT_PERFIS.md`.

## 18–19. Issues e correcções

`docs/SPRINT18_ISSUES.md`; UI médicos com indicador “Pendente de configuração”.

## 20. Impressão

Validar localmente (A4/térmica) — **NECESSITA AJUSTE** em ambiente físico.

## 21. Permissões

Cobertas por testes Sprint 15/17/18.

## 22. Migrations

Nenhuma nova; `makemigrations --check` OK.

## 23–25. Testes, build, lint

- **285** testes pytest (279 + 6 Sprint 18), `--reuse-db`.
- Build frontend OK; lint 0 erros.

## 26–27. Riscos e pendências

- Clínica ainda não devolveu preços confirmados.
- Executar apply de catálogo e lab após backup.

## 28. Decisão piloto

**APROVADO COM RESSALVAS**

## 29. Sprint 19

1. Importar preços após CSV validado.
2. Completar `MedicoPerfil`.
3. Piloto presencial receção + laboratório.
4. Impressão e hardware.
5. Avaliar módulos clínicos (ecografia) só com preços fechados.

## Comandos novos

- `validate_precos_validacao_clinica`
- `sprint18_backup_db`
- `sprint18_audit_reports`
- `backend/scripts/run_sprint18_pilot.bat`
