# Sprint 25 — Laboratory Workflow Hardening

**Data:** 2026-08-23  
**Base:** `docs/LABORATORY_WORKFLOW_AUDIT.md`  
**Estado alvo:** `LABORATORY_READY_FOR_UAT`

## Objectivo

Hardening operacional do perfil LABORATÓRIO sem criar LIS, sem redesign global e sem alterar a arquitectura clínica desnecessariamente.

## Decisões

### Regularização (P0)

- Pedidos com `estado_faturacao = AGUARDA_REGULARIZACAO` **não podem** iniciar processamento (`POST …/start/`).
- Mensagem: «Este exame aguarda regularização na Receção.»
- Pedido permanece visível; lab vê apenas estado mínimo (`Aguarda regularização` / `Regularizado`).
- Sem bypass de urgência (não existia regra implementada).
- Lab **não** cria fatura, pagamento nem vê montantes.

### Receção

- UI em `/reception/lab-orders` (também no sub-nav de Faturação).
- Fluxo: ver exame → Abrir faturação (existente) → Marcar regularizado.
- `mark-lab-order-billed` é **idempotente** (`already_regularized`).
- Marcar regularizado **não** cria pagamento.

### Validar vs Publicar

- **Validar** = disponibiliza ao médico (inalterado).
- Botão «Publicar ao médico» renomeado para **«Marcar como entregue»** (estado `ENTREGUE`).
- API `publish` preservada (legado).

### Conclusão clínica

- `concluir_exame` já **não** marca `PedidoLaboratorio.estado = CONCLUIDO`.
- O pedido clínico só fica `CONCLUIDO` na **validação** do resultado.
- Copy operacional: «Processamento concluído» / «Aguarda validação».

### Exames directos / walk-in

- **Não implementados** nesta sprint.
- Motivo: `PedidoLaboratorial.consulta` é FK obrigatória; exigir-ia refactor estrutural.
- Documentado como decisão clínica necessária (P2).

### Impressão

- `LabResultPrint` ligado ao detalhe do resultado.
- Impressão só disponível após `VALIDADO` / `ENTREGUE`.
- Reimpressão não altera estado nem cria cobrança.

### Parâmetros do catálogo

- `TipoExameLaboratorio` não pré-preenche formulário nesta sprint (estrutura sem parâmetros multi-linha confiáveis).
- Resultado textual (`conclusao`) preservado.

## Alterações principais

| Área | Ficheiros |
|---|---|
| Gate billing | `apps/laboratory/billing.py`, `laboratory_service.py` |
| Prioridade | `apps/laboratory/ordering.py` + `PRIORITY_ORDER` |
| Serializers | identificação utente + `estado_faturacao_*` |
| Filtros/pesquisa | `filters.py` (`q`, `estado_faturacao`) |
| Receção API | idempotência + filtro estado |
| FE lab | tabela, filtros, detalhe, print, copy |
| FE receção | `PendingLabOrdersPage` |
| Testes | `test_laboratory_hardening_sprint25.py` |

## Gates

Executar suite completa após implementação (ver chat / CI).

## UAT

Ver `docs/UAT_LABORATORIO_FINAL.md`.
