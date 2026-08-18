# Sprint 21 Fase 4 — Eventos bloqueados (66)

Sem identificadores pessoais. Ficha privada: `backend/data/private/sauvida_migration/eventos_bloqueados_validacao.xlsx` (gitignored).

## Categorias (motivo primário)

| Categoria | Quantidade |
| --- | ---: |
| PACIENTE_BLOQUEADO | 48 |
| LAB_AMBIGUO | 13 |
| DATA_SUSPEITA | 4 |
| DESCRICAO_INSUFICIENTE | 1 |
| OUTRO | 0 |
| **Total** | **66** |

Prioridade do motivo primário: DATA_SUSPEITA > LAB_AMBIGUO > PACIENTE_BLOQUEADO > DESCRICAO_INSUFICIENTE > OUTRO.

## Desbloqueio após duplicados

**48** eventos têm *apenas* `PACIENTE_BLOQUEADO`. Depois de `PESSOAS_DIFERENTES` ou `IMPORTAR_SEPARADAMENTE` (ou `MESMA_PESSOA` no utente canónico), podem entrar no lote `SAUVIDA-HIST-V1-REVIEW`.

Os 13 labs ambíguos e as 4 datas exigem decisão própria. 1 evento sem data interpretável permanece bloqueado até a clínica confirmar a data.

Dry-run actual `--reviewed-only --batch-id SAUVIDA-HIST-V1-REVIEW` (sem decisões preenchidas): **0** eventos a importar, 66 ainda bloqueados.
