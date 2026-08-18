# Sprint 21 Fase 4 — Relatório

**Projecto:** SGCS — Clínica SauVida  
**Data:** 2026-08-17  
**Lote auditado:** `SAUVIDA-HIST-V1`  
**Nova importação / rollback real / stock:** **não executados**  
**Estado:** `VALIDACAO_POS_MIGRACAO_CONCLUIDA`

## 1. Auditoria batch

156 Patient + 338 PatientHistory (156 REGISTO + 182 clínicos) + 156 AuditLog. 0 órfãos, 0 leakage. Ver `docs/SPRINT21_FASE4_BATCH_AUDIT.md`.

## 2. Reconciliação rollback

338 = 156 auxiliares `REGISTO` + 182 actos clínicos. Não é duplicação nem erro. Rollback enriquecido com a decomposição. Ver `docs/SPRINT21_FASE4_ROLLBACK_RECONCILIATION.md`.

## 3. Integridade pacientes

156/156 com `migration_id` único, source/batch correctos, `dados_verificados=false`, 0 bloqueados importados, nada inventado. Ver `docs/SPRINT21_FASE4_PATIENT_INTEGRITY.md`.

## 4. Integridade histórico

182/182 ligados ao utente do lote, provenance completa, 0 órfãos. Ver `docs/SPRINT21_FASE4_HISTORY_INTEGRITY.md`.

## 5. Financeiro isolado

0 faturas/pagamentos/recibos/caixa do lote. Valores só no metadata clínico. Ver `docs/SPRINT21_FASE4_FINANCIAL_ISOLATION.md`.

## 6. Pacientes bloqueados

38 (todos nos 23 pares). Ficha: `pacientes_bloqueados_validacao.xlsx` (privada).

## 7. Duplicados

23 pares. Ficha presencial: `duplicados_validacao_sauvida.xlsx`. Sem fusão automática. `INDETERMINADO` = não importar neste lote.

## 8. Eventos bloqueados

66 = 48 só paciente + 13 lab ambíguo + 4 data + 1 sem data. 48 desbloqueáveis após decisão de duplicados. Ver `docs/SPRINT21_FASE4_BLOCKED_EVENTS.md`.

## 9. Laboratório

4 estruturados e 39 textuais já importados. 13 eventos ambíguos (2 descrições distintas) aguardam o técnico. `MANTER_TEXTUAL` é válido. Ficha: `laboratorio_validacao_historica.xlsx`.

## 10. Médicos

3 nomes históricos, 0 utilizadores SGCS sugeridos. Ficha: `medicos_validacao_historica.xlsx`. Sem criação automática de contas.

## 11. Stock

55 candidatos. Ficha enfermeira: `stock_urgencia_validacao.xlsx`. Não importado.

## 12. UX de confirmação

Aviso e acção «Confirmar dados» já na ficha. Confirmação e PATCH de Receção **preservam** source/batch/`migration_id` (teste + reforço no endpoint). Não se confirmou nenhum utente real nesta fase.

## 13. Runbook produção

`docs/RUNBOOK_MIGRACAO_HISTORICA_PRODUCAO.md`.

## 14. Testes

Novos testes em `test_historical_fase4.py` (auditoria, rollback, órfãos, financeiro, stock, revisão, provenance). Suite completa: **362 passed**, **2 failed** pré-existentes na Receção (médico indisponível). Receção não alterada.

## 15. Gates

- `manage.py check`: OK  
- `makemigrations --check`: OK  
- Frontend: não alterado nesta fase  

## 16. Riscos

- 38 utentes e 66 eventos continuam fora do SGCS.  
- 173 eventos sem paciente só em arquivo.  
- 48 eventos dependem da validação presencial dos duplicados.  
- Relatórios clínicos podem mostrar montantes históricos na cronologia; faturação/caixa não.

## 17. Estado final

**VALIDACAO_POS_MIGRACAO_CONCLUIDA**
