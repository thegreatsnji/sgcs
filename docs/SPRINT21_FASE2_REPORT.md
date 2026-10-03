# Sprint 21 Fase 2 — Relatório

**Projecto:** SGCS — Clínica SauVida  
**Data:** 2026-08-17  
**Âmbito:** priorização da revisão, pipeline `--apply` idempotente, proveniência, rollback, aviso na ficha, dry-run final.  
**Fora de âmbito nesta tarefa:** execução real de `--apply` (aguarda validação clínica).

## Entregas

- Reclassificação bloqueante vs. não bloqueante (CSVs privados).
- `--apply --patients-only` / `--history-only` / `--skip-blocked` / `--batch-id` / `--actor-email` / `--confirm-backup`.
- `rollback_sauvida_history`.
- `backup_sauvida_pre_apply`.
- Paciente histórico: `metadata` + nascimento/telefone/sexo opcionais **só no modelo** (o registo operacional da receção continua a exigir dados).
- Aviso discreto na ficha: «Dados provenientes do registo anterior da clínica…» + «Confirmar dados».

## Dry-run final (`SAUVIDA-HIST-V1`, skip-blocked)

156 pacientes prontos, 38 bloqueados, 182 eventos prontos, 66 eventos bloqueados. BD inalterada.

## Gates

- `manage.py check` — sem problemas
- `makemigrations --check` — sem alterações extra (migration `patients.0002_sprint21_fase2_historical_import` aplicada)
- Testes Sprint 21 Fase 1+2: incluídos na suite
- `pytest -q --reuse-db` — **352 passed**, **2 failed** pré-existentes na Receção (médico indisponível); Receção não foi alterada
- Frontend: `npm run lint` (0 erros, avisos pré-existentes) e `npm run build` OK

## Estado

**AGUARDA_VALIDACAO** — pipeline pronto; apply só após autorização e backup válido.
