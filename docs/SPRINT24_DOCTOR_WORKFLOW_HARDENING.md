# Sprint 24 — Hardening do fluxo do médico

**Data verificação final:** 2026-08-23  
**Estado:** `DOCTOR_READY_FOR_UAT`

## Objectivo

Fechar os riscos P0 da auditoria do fluxo clínico, mantendo separação entre
informação clínica e financeira — sem redesign global.

## Entregue

- Fila e dashboard do MÉDICO limitados às consultas atribuídas ao próprio.
- `billing.view` removido do papel MÉDICO; menus/tabs financeiros ocultos por papel.
- Prontuário expõe apenas estado financeiro operacional (`codigo`/`label`), sem montantes.
- Resultados laboratoriais não validados: só estado (“Aguarda validação” / “Em processamento”);
  valores clínicos apenas em `VALIDADO` / `ENTREGUE`.
- Vitais do check-in: cartão “Sinais vitais da triagem”; cópia só com “Usar como base”.
- Pedido clínico laboratorial: catálogo (sem preço) + texto livre; nasce em
  `AGUARDA_REGULARIZACAO` — **não** cria fatura/pagamento/recibo.
- Receção: listar pedidos pendentes e marcar regularização (flag operacional).
- SOAP com autosave (debounce ~1,5 s); não conclui nem cria efeitos laterais.
- Prescrição na tab da consulta com `consulta_id` injectado.
- Seguimento: **recomendação de retorno** — não cria marcação automática.
- Conclusão de consulta idempotente.

## API

- `GET /api/v1/appointments/laboratory-catalog/`
- `GET /api/v1/reception/pending-clinical-lab-orders/`
- `POST /api/v1/reception/mark-lab-order-billed/{id}/`

## Dados

`PedidoLaboratorio`: FK opcional `servico`; `estado_faturacao`
(`AGUARDA_REGULARIZACAO` | `REGULARIZADO` | `NAO_APLICAVEL`).

Migração: `appointments/0005_pedidolaboratorio_billing_bridge.py`.

## Comportamento lab → Receção (verificado)

1. Médico pede exame → pedido clínico criado.
2. **Não** cria fatura, pagamento nem recibo automaticamente.
3. Receção vê pedido em `pending-clinical-lab-orders`.
4. Receção factura pelo fluxo de faturação existente (catálogo/preço).
5. `mark-lab-order-billed` apenas marca `REGULARIZADO` (idempotente ao reenviar).
6. Dupla cobrança automática pelo bridge: **não** — a faturação continua manual na Receção.

## Seguimento (verificado)

UI: “Recomendar seguimento” + aviso de que **não cria consulta automaticamente**.
Persiste `Seguimento` no prontuário; Receção não recebe marcação nova por este caminho.

## Gates — verificação final (2026-08-23)

| Gate | Resultado |
|---|---|
| `python manage.py check` | OK (0 issues) |
| `makemigrations --check` | OK (No changes detected) |
| `pytest -q --reuse-db` | **484 passed**, 2 skipped, 0 failed |
| `npm run build` | OK |
| `npm run lint` | 0 errors, 11 warnings (1 novo em SOAPForm deps; resto pré-existente) |

Baseline pré-Sprint 24: 475 passed / 2 skipped.  
Delta: +9 testes (hardening médico); **0 regressões**.

## Regressão Receção

Suite completa inclui `reception` (atribuição médico, check-in, fila, faturação).
Estado `RECEPTION_READY_FOR_UAT` preservado (0 failed na suite).

## Testes de hardening

`apps/appointments/tests/test_doctor_workflow_hardening.py`:

- fila exclusiva / não atribuídos excluídos
- MÉDICO 403 em `/billing/invoices/`
- lab não validado sem valores; validado com valores
- triagem exposta sem cópia silenciosa
- SOAP draft persiste
- prescrição com `consulta_id`
- pedido lab `AGUARDA_REGULARIZACAO`
- conclusão idempotente
- seed sem `billing.view` no MÉDICO

## UAT presencial

`docs/UAT_MEDICO_FINAL.md` — 14 tarefas práticas.
