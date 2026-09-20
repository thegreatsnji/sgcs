# Auditoria End-to-End — Perfil RECECIONISTA (SauVida)

**Data:** 2026-08-20  
**Pergunta:** Uma rececionista da Clínica SauVida consegue fazer o trabalho diário sem ajuda do programador?  
**Estado:** `RECEPTION_READY_FOR_UAT`

---

## Resumo executivo

Os fluxos principais (walk-in, existente, importado, marcação+chegada, faturação integral/parcial/redução, fila, privacidade) estão **operacionais**. As duas falhas pytest historicamente atribuídas a «médico indisponível» foram **reclassificadas**: fixture de teste sem médico (não bug de produção). Comportamento sem médico é **seguro** (utente e pagamento preservados).

---

## Cenário A — Walk-in novo

| Passo | Acção |
|---|---|
| 1 | Atendimento rápido |
| 2 | Pesquisa (sem resultado) |
| 3 | Registo novo utente |
| 4 | Continua triagem / check-in |
| 5 | Faturação (serviço) |
| 6 | Pagamento + recibo |
| 7 | Atribuir médico → fila / consulta EM_ESPERA |

**Duplicados:** paciente/serviço/fatura/check-in/consulta — cobertos por teste E2E (1 de cada).  
**Passos ≈** 8–12 cliques. **Fricção:** `ACEITAVEL` (registo separado do atendimento é consciente).

---

## Cenário B — Utente existente

Pesquisa → seleccionar → triagem → faturação → pagamento → médico.  
Sem reintrodução de dados demográficos. **SEM_FRICCAO**.

---

## Cenário C — Histórico importado

Ficha → aviso migração → completar telefone/morada → Confirmar dados → Novo atendimento (`?paciente=`) → faturação → fila.  
Provenance (`migration_id`, `import_batch`) e PatientHistory preservados; escrita clínica bloqueada (Sprint 23.3). **ACEITAVEL**.

---

## Cenário D — Marcação + Confirmar chegada

Marcações → Confirmar chegada → `ReceptionService.check_in` → faturação se aplicável → encaminhar.  
Idempotente; não duplica marcação/consulta/check-in. **SEM_FRICCAO**.

---

## Cenários E–I — Faturação

| Cenário | Resultado |
|---|---|
| E Integral 10k | Pago 10k, saldo 0, recibo, resumo recebe no dia |
| F Redução 10k→8k | Faturado/recebido 8k; catálogo permanece 10k |
| G Parcial 6k + 4k | Saldo intermédio 4k; `com_saldo`; 2 recibos |
| H Overpay | Backend + frontend bloqueiam; sem pagamento inválido |
| I Cancelar | Soft cancel; fora de saldo activo; registo preservado |

---

## Cenário J — Fila

Posições «1.º / 2.º na fila»; espera «cerca de N min» / «sem estimativa»; triagem amarela/verde; «Prioridade alta»; «Chamado». Sem `#1` / `~90` / enums crus na UI principal.

---

## Cenário K — Sem médico (obrigatório)

### Causa das 2 falhas pytest

| Teste | Causa real |
|---|---|
| `TestConsultaFluxo::test_handoff_cria_consulta_em_espera` | **B — fixture desactualizada**: não criava `MEDICO`; `assign_to_doctor` exige médico disponível |
| `TestWaitingQueue::test_assign_to_doctor` | **B — idem** |

**Não** é crash de produção nem perda de dados. Regra de negócio intencional: encaminhar só com médico seleccionado/disponível.

### Comportamento real

1. API devolve erro controlado («Seleccione um médico disponível…»).
2. Utente permanece em **WAITING** na fila (validação **antes** de alterar estados).
3. Pagamento/recibo **intactos**.
4. Nenhuma consulta criada.
5. UI: aviso se não houver médicos / todos em consulta; botão de atribuição desactivado sem seleção.

### Correcção

- Testes actualizados com `doctor_user` + `doctor_id`.
- Serviço: resolve médico antes de mutar fila/check-in.
- Painel: mensagem operacional quando não há médicos.

---

## Cenário L — Privacidade

Receção: escrita alergias/crónicas/observações **403**; diagnóstico/notas omitidos nas consultas; lab results **403**; history read-only. Médico mantém escrita clínica.

---

## Cenário M — Resumo financeiro

Períodos hoje/semana/mês/personalizado. Recebido por `data_pagamento`. Histórico financeiro migrado **excluído**.

---

## Cenário N — Pesquisa

Pacientes: nome, telefone, código. Faturas: nome, `FAT-…`, n.º processo. 0 / 1 / N resultados suportados.

---

## Cenário O — Responsividade

Fluxos pensados para portátil ~1366×768. Sem redesign nesta sprint. Overflow crítico não identificado no código dos fluxos principais; validar no UAT presencial no ecrã real da Receção.

---

## Navegação RECECIONISTA

Painel · Atendimento rápido · Fila · Faturação · Pacientes · Marcações.  
**Sem** Notificações, Financeiro, Stock, Laboratório, Administração, Configurações, Relatórios executivos.

---

## Copy

Fila e badges já em PT institucional. Hífens em `PAC-` / `FAT-` legítimos. Sem limpeza massiva adicional necessária nesta sprint.

---

## Fricção residual (não bloqueante)

| Item | Classe |
|---|---|
| Walk-in: registo → voltar ao atendimento | ACEITAVEL |
| Pagamento parcial: 2ª visita a Faturação | ACEITAVEL |
| Sem médico: espera operacional | ACEITAVEL (mensagem clara) |
| Marcações na ficha (gestão completa) | MELHORAR_DEPOIS (P3) |

**Nenhum BLOQUEANTE.**

---

## Testes

`apps/reception/tests/test_reception_e2e_uat.py` — walk-in, existente, importado, chegada, faturação, redução, parcial/overpay, cancelar, fila, sem médico, privacy.

---

## Gates (ver Sprint 23.4 report)

Documentados em `docs/SPRINT23_4_RECEPTION_FINAL_REPORT.md`.
