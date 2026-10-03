# Sprint 21 Fase 1 — Relatório

**Projecto:** SGCS — Clínica SauVida  
**Data:** 2026-08-17  
**Âmbito:** auditoria, staging, limpeza, normalização, deduplicação, mapeamento, validação e dry-run sobre o Excel histórico real.  
**Fora de âmbito:** `--apply`, faturas modernas, stock físico, frontend, novos modelos Django.

## Entregas

- App `apps.data_migration` (sem modelos novos; proveniência `MIGRACAO_EXCEL_SAUVIDA` via `PatientHistory` existente).
- Scripts: `audit_sauvida_historical_excel.py`, `build_sauvida_historical_staging.py`.
- Comando: `python manage.py import_sauvida_history --dry-run` (`--apply` recusado).
- `.gitignore` para `backend/data/private/` e artefactos de pacientes.
- Testes com Excel **fictício** (19 testes).
- Documentação: `MIGRACAO_HISTORICA_AUDITORIA.md`, `MIGRACAO_HISTORICA_DRY_RUN.md`, `MIGRACAO_HISTORICA_REVISAO.md`, este relatório.

## Privacidade

Excel real e CSVs derivados **fora do Git**. Relatórios sem nomes, telefones ou outros identificadores. SHA256 do original (inalterado): `bfd987eec4a82c454d1a4519d460ef64fcad16b91dcb47af95fe6a6847ce6822`.

## Auditoria real (agregado)

13 folhas, 651 linhas de origem, 194 candidatos a paciente (191 nomes únicos normalizados), 421 eventos históricos, 566 linhas financeiras de acto (sem totais `SOMA GERAL`), 55 candidatos a stock de referência com `quantidade_inicial` vazia, 3 médicos históricos, 739 itens de revisão.

Pormenor em `docs/MIGRACAO_HISTORICA_AUDITORIA.md`.

## Dry-run

Comando só de leitura. 194 candidatos, 194 estimados novos na BD actual, 0 correspondências seguras, 0 duplicados com utentes SGCS existentes. Contagens da BD inalteradas (Patient 10, User 12, Fatura 5, etc.). `--apply` não foi executado e permanece desactivado.

## Recomendação Fase 2

1. Completar `decisao` em `migracao_revisao_manual.csv` (prioridade: linhas sem paciente, 181 utentes incompletos, 22 pares só por nome).
2. Direcção clínica confirma mapeamentos laboratoriais; **não** aceitar `AMBIGUO` / `SEM_CORRESPONDENCIA` automaticamente (só 6 eventos `ALINHADO`).
3. Enfermagem confirma nomes canónicos de medicamentos; **não** carregar `quantidade_inicial` sem contagem física.
4. Associar os 3 médicos históricos a utilizadores `MEDICO` existentes, ou deixá-los por mapear — **não** criar contas na importação.
5. Datas suspeitas (5) ficam como na fonte até indicação da clínica.
6. Só então implementar `--apply` transaccional, por lote, com `import_batch` e rollback, **sem** gerar faturas/pagamentos modernos nem fundir utentes só por nome.

## Gates (ambiente Docker SGCS)

- `python manage.py check` — sem problemas
- `python manage.py makemigrations --check` — sem alterações de modelo
- Testes Sprint 21 (`apps/data_migration/tests/test_historical_migration.py`) — **19 passed**
- `pytest -q --reuse-db` — **338 passed**, **2 failed** pré-existentes e sem relação com esta sprint:
  - `apps/appointments/tests/test_appointments.py::TestConsultaFluxo::test_handoff_cria_consulta_em_espera`
  - `apps/reception/tests/test_reception.py::TestWaitingQueue::test_assign_to_doctor`
  - Causa: «Seleccione um médico disponível para este utente.» Código de receção **não** foi alterado.
- `pytest-django` limitado a `<4.12` para compatibilidade com Django 5.1

Frontend não foi alterado.
