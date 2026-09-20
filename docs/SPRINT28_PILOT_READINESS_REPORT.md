# Sprint 28 — Pilot Readiness Report

**Data:** 2026-08-25  
**Tipo:** auditoria de prontidão (sem features novas)  
**Baseline entrada:** 530 passed · 2 skipped · 0 failed  
**Estado:** `PILOT_READY_FOR_UAT`

## Objectivo

Verificar integração entre perfis, ambiente, demo, backups, segurança, impressão, performance, erros e continuidade — e consolidar UAT presencial.

## Documentos produzidos

| Documento | Função |
|---|---|
| [PILOT_READINESS_AUDIT.md](PILOT_READINESS_AUDIT.md) | Achados técnicos da auditoria |
| [UAT_PILOTO_SAUVIDA_MASTER.md](UAT_PILOTO_SAUVIDA_MASTER.md) | Roteiro presencial integrado |
| [PILOT_GO_NO_GO_CHECKLIST.md](PILOT_GO_NO_GO_CHECKLIST.md) | Critérios go-live |
| [DEMO_DATA.md](DEMO_DATA.md) | Actualizado: demo vs real, reset, gap stock |

## Ajuste mínimo (não-feature)

- `seed_demo`: faturação demo passa a usar **Receção** (não Director), alinhado ao RBAC Sprint 27.

## Achados críticos

1. **Backup Settings API = stub** (`BackupService` / Celery `status: stub`, `tamanho_bytes=0`). Backup real = `pg_dump` documentado.
2. **Compose = development** (sem TLS). Piloto com dados reais exige `production` + HTTPS.
3. **seed_demo** não cria stock; UAT Enfermagem deve criar itens fictícios.
4. Impressão física e medição de tempos: pendentes da sessão presencial.

## Integração (resumo)

Fluxos Receção↔Enfermagem↔Médico↔Lab↔Director cobertos por testes de hardening (23–27) + e2e Receção. Prova presencial: master UAT.

## Qualidade

| Gate | Resultado |
|---|---|
| `manage.py check` | OK (0 issues) |
| `makemigrations --check` | OK (No changes detected) |
| `pytest -q --reuse-db` | **530 passed, 2 skipped, 0 failed** |
| `npm run build` | OK |
| `npm run lint` | 0 errors (10 warnings pré-existentes) |

## Conclusão

| Pergunta | Resposta |
|---|---|
| Pode começar UAT presencial em ambiente demo? | **Sim** — `PILOT_READY_FOR_UAT` |
| Pode go-live com dados reais hoje? | **Só após** checklist GO (HTTPS, backup real, impressão, contas reais) |

**Próximo passo operacional:** executar `UAT_PILOTO_SAUVIDA_MASTER.md` na clínica / sala de formação.
