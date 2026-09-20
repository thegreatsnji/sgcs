# Auditoria — Faturação (Receção / RECECIONISTA)

**Data:** 2026-08-20  
**Âmbito:** fluxo de Faturação para o perfil RECECIONISTA no SGCS SauVida.  
**Estado:** `BILLING_AUDIT_COMPLETE`  
**Código nesta tarefa:** nenhuma alteração (só documentação).

---

## 1. Inventário do que existe

### Frontend (rotas sob `billing.view`)

| Rota | Página | Função aparente |
|---|---|---|
| `/billing` | Dashboard billing | KPIs gerais (Receção entra normalmente pela lista) |
| `/billing/invoices` | Lista de faturas | Entrada do menu **Faturação** |
| `/billing/invoices/new` | Nova fatura | Criar + redução + (opcional) ir a pagar |
| `/billing/invoices/:id` | Detalhe | Pagamento / confirmar / ver totais |
| `/billing/payments` | Lista pagamentos | Histórico de pagamentos |
| `/billing/receipts` | Lista recibos | Histórico de recibos |
| `/billing/receipts/:id` | Detalhe / impressão | ORIGINAL / SEGUNDA VIA |
| `/billing/services` | Catálogo | Ver serviços (editar preço oficial bloqueado) |
| `/billing/quotes` | Orçamentos | Rotas existem; Receção **sem** `billing.quote` |
| `/billing/reducoes/pendentes` | Autorizações | Pedidos de redução acima do limite |
| `/billing/history` | Histórico por paciente | Exige ID numérico manual |

**Menu Receção:** `Faturação` → `/billing/invoices` (entre Fila e Pacientes).

**Dashboard Receção:** `ReceptionFinancialSummary` → `GET /api/v1/billing/resumo-operacional/`.

### Backend (principais)

| Endpoint | Permissão típica | Notas |
|---|---|---|
| `GET/POST /api/v1/billing/invoices/` | view / create | Criar fatura |
| `GET/PATCH /api/v1/billing/invoices/{id}/` | view / edit | Detalhe; desconto de fatura se editável |
| `POST .../invoices/{id}/items/` | edit | Adicionar item (+ redução na criação do item) |
| `POST .../invoices/{id}/cancel/` | edit | Cancelar fatura (soft `CANCELADA`) — **sem UI** |
| `GET/POST /api/v1/billing/payments/` | view / payment | Registar pagamento |
| `POST .../payments/{id}/confirm/` | payment | Confirmar → emite recibo |
| `GET /api/v1/billing/receipts/` | receipt | Lista |
| `GET .../receipts/{id}/impressao/?segunda_via=1` | receipt | Impressão; marca SEGUNDA VIA |
| `GET/POST /api/v1/billing/services/` | view / create | Catálogo |
| `PATCH /api/v1/billing/services/{id}/` | edit | Preço oficial **só Admin** |
| `GET /api/v1/billing/patient-history/{id}/` | view | Resumo + faturas do paciente |
| `GET /api/v1/billing/resumo-operacional/` | view | Totais balcão por período |
| `GET/POST /api/v1/billing/reducoes/` | view / create | Autorização de redução |

**Não existe:** DELETE de fatura/pagamento; remoção de item via API; anulação/reembolso de pagamento via HTTP.

### RBAC RECECIONISTA (seed)

**Tem:** `billing.view`, `create`, `edit`, `payment`, `receipt`, `print`.  
**Não tem:** `billing.delete`, `billing.export`, `billing.quote`, `finance.*`, `reports.*`.

### Estados

| Entidade | Estados |
|---|---|
| Fatura | `PENDENTE`, `PARCIAL`, `PAGA`, `CANCELADA` |
| Pagamento | `PENDENTE`, `PROCESSADO`, `CONFIRMADO`, `REEMBOLSADO` (enum; **sem fluxo UI/API de reembolso**) |
| Recibo | `segunda_via` boolean (ORIGINAL vs SEGUNDA VIA) |

### Modelos-chave (preço / dinheiro)

| Campo | Significado |
|---|---|
| `Servico.preco` | Preço oficial do **catálogo** |
| `ItemFatura.preco_oficial` | Snapshot oficial na linha |
| `ItemFatura.preco` | Preço **cobrado** |
| `ItemFatura.valor_reducao` | Oficial − cobrado (por linha) |
| `Fatura.total` | Soma dos subtotais **cobrados** (− desconto fatura) |
| `Fatura.total_pago` | Soma pagamentos `CONFIRMADO` (propriedade) |
| Saldo | **Derivado:** `max(total − total_pago, 0)` — **não** é campo persistido |

---

## 2. O que a rececionista consegue fazer hoje em Faturação

| Acção | Existe na UI? | Funciona para RECECIONISTA? | Notas |
|---|---|---|---|
| Criar fatura | SIM | SIM | Lista + Atendimento rápido |
| Adicionar serviço | SIM | SIM | Na criação |
| Remover item **antes** de emitir | SIM (só UI create) | SIM | **Sem** endpoint de remoção pós-criação |
| Aplicar redução | SIM | SIM | Na criação do item; limite % + motivo; acima do limite → autorização Direção |
| Alterar preço do catálogo | NÃO (bloqueado) | API rejeita para Receção | Correcto |
| Receber pagamento integral | SIM | SIM | Registar → Confirmar |
| Receber pagamento parcial | SIM | SIM | Qualquer valor > 0; estado `PARCIAL` |
| Segundo (e N-ésimo) pagamento | SIM | SIM | Enquanto saldo > 0 e fatura editável |
| Consultar Total / Pago / Saldo | PARCIAL | SIM | Forte na criação; no detalhe «Pendente» em vez de Saldo explícito |
| Emitir recibo | SIM | SIM | Ao confirmar pagamento |
| Imprimir recibo | SIM | SIM | `?imprimir=1` / botão |
| Segunda via | SIM | SIM | Não cria novo pagamento |
| Cancelar / anular fatura | **NÃO (UI)** | API+RBAC SIM | `POST .../cancel/` existe |
| Anular pagamento | **NÃO** | NÃO | Sem endpoint operacional |
| Pesquisar faturas | **NÃO** | Lista sem search | API filtra `paciente`/`estado` sem UI |
| Filtrar por período / saldo | **NÃO** | — | |
| Histórico por paciente | PARCIAL | SIM | `/billing/history` com ID manual; tab Pacientes fraca |
| Lista «quem deve» | **NÃO** | Só agregado no resumo | Lacuna |
| Orçamentos | Rotas existem | **NÃO** (`billing.quote`) | |

---

## 3. Fluxo normal

### Caminho balcão (Atendimento rápido)

```
Paciente (passo 1)
→ Triagem / check-in (passo 2)
→ «Criar fatura e cobrar» (passo 3)
→ /billing/invoices/new?paciente={id}&pagar=1&tipo={CONSULTA|CONTROLE}&retorno=…
→ Seleccionar serviço(s) (+ redução opcional)
→ Guardar e receber pagamento
→ Detalhe: Registar pagamento → Confirmar e emitir recibo
→ Impressão recibo
→ Continuar: notificar médico (passo 4) — exige fatura do dia totalmente paga
```

**≈ 8–9 acções/ecrãs** no happy path.

### Deep-link: o que é reutilizado vs duplicado

| Dado | Reutilizado? |
|---|---|
| Paciente | SIM (`?paciente=`) — mas o selector continua editável |
| Tipo visita (`tipo=`) | **NÃO lido** em `InvoiceCreatePage` — serviço **não** pré-seleccionado |
| Consulta / marcação | **NÃO** no URL do atendimento |
| Retorno ao workflow | SIM (`retorno`) |

**Duplicação principal:** após escolher paciente e tipo de visita na Receção, a Receção volta a pesquisar o **serviço** (e pode mudar o paciente).

### Caminho menu Faturação

Lista → Nova fatura → escolher paciente + serviços → pagamento (2 passos) → recibo.  
Sem triagem; mais cliques de pesquisa.

### Marcações

`Fatura.consulta` (OneToOne opcional) existe no modelo; o fluxo operacional da Receção é **paciente-cêntrico**, não ligado a «Confirmar chegada». Sem faturação automática a partir de Marcações.

---

## 4. Preço oficial vs preço cobrado

| Regra | Confirmado? |
|---|---|
| Catálogo `Servico.preco` = oficial | SIM |
| Linha guarda `preco_oficial` + `preco` (cobrado) | SIM |
| Redução não altera catálogo | SIM (copy no resumo + backend) |
| Cobrar acima do oficial | REJEITADO + auditoria |
| Redução auditada (`reduzido_por`, motivo, %, acções audit) | SIM |
| Item histórico preserva preços após emissão | SIM (snapshot na linha) |

**Exemplo:** oficial 5 000 → cobrado 4 000 → `valor_reducao` 1 000; catálogo permanece 5 000.

---

## 5. Pagamento parcial

| Regra | Confirmado? |
|---|---|
| Saldo = total cobrado − pagos CONFIRMADO | SIM |
| Parcial ≠ redução | SIM (`test_saldo_nao_e_desconto`) |
| Segundo pagamento possível | SIM |
| Recibo por cada pagamento confirmado | SIM (1:1 `Pagamento`↔`Recibo`) |
| Saldo 0 → estado `PAGA` | SIM |

**Exemplo:** fatura 10 000 / pago 6 000 / saldo 4 000 / redução 0 — coerente.

**Risco:** API **não** impede pagamento > saldo restante (overpay).

---

## 6. Redução + pagamento parcial

| Grandeza | Valor esperado | Regra sistema |
|---|---|---|
| Preço oficial | 10 000 | `preco_oficial` / subtotal oficial |
| Preço cobrado / faturado | 8 000 | `Fatura.total` |
| Redução | 2 000 | `valor_reducao` |
| Pago agora | 5 000 | pagamento CONFIRMADO |
| Saldo | **3 000** | sobre cobrado, **não** sobre oficial |

Confirmado pela lógica de `_recalcular_fatura` + `total_pago` + testes de resumo/redução.

---

## 7. Pagamento (campos e UX)

**Fluxo UI:** Registar (`PENDENTE`) → Confirmar (`CONFIRMADO` + recibo). Dois passos.

**Visibilidade Totals:**

| Ecrã | Total | Pago | Saldo |
|---|---|---|---|
| Criação (`InvoiceSummaryPanel`) | SIM («Total a cobrar») | se pago>0 | SIM |
| Detalhe fatura | SIM | via pagamentos | «Pendente» (rótulo fraco) |
| Recibo impresso | SIM | SIM | SIM (se config) |

**Métodos existentes:** `DINHEIRO`, `TRANSFERENCIA`, etc. (enums). UI do formulário mostra **códigos técnicos**, não labels PT — fricção menor, sem necessidade clínica de novos métodos.

---

## 8. Recibo

| Aspecto | Estado |
|---|---|
| Emissão | Ao confirmar pagamento |
| Numeração | `REC-{ano}-{seq}` única |
| Paciente / serviços / valores | No contexto de impressão |
| Redução / saldo / operador / data | Presentes no documento |
| ORIGINAL | Implícito (`segunda_via=False`; banner «ORIGINAL» pouco explícito) |
| SEGUNDA VIA | Botão + query `segunda_via=1` |
| Reimprimir = novo pagamento? | **NÃO** |

---

## 9. Cancelamento / anulação

| Acção | API | UI Receção | Comportamento |
|---|---|---|---|
| Cancelar fatura | SIM (`billing.edit`) | **NÃO** | Soft `CANCELADA`; bloqueado se `PAGA`; auditado |
| Anular / reembolsar pagamento | **NÃO** | **NÃO** | Enum `REEMBOLSADO` sem fluxo |
| Apagar registos | NÃO | NÃO | Correcto |

**Não implementar nesta auditoria** — documentado como lacuna UI (cancel fatura) e lacuna de produto (anular pagamento).

---

## 10. Pesquisa e filtros

| Necessidade | Backend | UI Receção |
|---|---|---|
| Por paciente | `?paciente=` | **Não** na lista de faturas |
| Por número | **Não** | Não |
| Por data / hoje | **Não** (lista) | Não |
| Por estado / saldo | `?estado=` | Não |
| Pagamentos do dia | Lista payments fraca | Sub-nav existe; sem filtro «hoje» |
| Agregado do dia | `resumo-operacional` | Dashboard Receção |

**Conclusão:** pesquisa operacional de faturas **insuficiente** para balcão; resumo cobre totais, não «encontrar a fatura X».

---

## 11. Saldos pendentes — «Quem ainda deve?»

| Mecanismo | Serve? |
|---|---|
| `saldo_pendente` no resumo operacional | Valor agregado do período — **não** lista de devedores |
| Histórico paciente | Por ID; mostra saldo do paciente |
| Lista faturas `estado=PARCIAL\|PENDENTE` | API possível; **UI sem filtro** |
| Tab Pagamentos no paciente | Liga a `/billing/history` **sem** `patient id` |

**Lacuna:** não há lista «saldos pendentes» / «quem deve» utilizável no balcão.

---

## 12. Faturação vs resumo financeiro

`GET /api/v1/billing/resumo-operacional/`:

| Métrica | Regra |
|---|---|
| Total faturado | `Fatura.total` por `emitida_em`, excl. `CANCELADA` |
| Total recebido | Pagamentos `CONFIRMADO` por `data_pagamento` |
| Saldo pendente | Soma saldos de faturas **emitidas no período** |
| Reduções | `ItemFatura.valor_reducao` |
| Histórico migrado | **Excluído** (não cria `Fatura`/`Pagamento`) |

**Coerência:** mesmas entidades/regras que o módulo billing; não misturar com `finance.*` nem PatientHistory migrado.

---

## 13. Segurança

| Controlo | Estado |
|---|---|
| Receção não altera preço oficial do catálogo | SIM |
| Receção não vê despesas/lucro (`finance.*`) | SIM |
| Receção não apaga pagamentos | SIM |
| Reduções auditadas + actor | SIM |
| Pagamento ≤ 0 rejeitado | SIM |
| Overpay (valor > saldo) | **Não bloqueado** — risco |
| Faturas antigas preservam preços de linha | SIM |
| Cancelar fatura paga | Bloqueado |
| UI não aplica `billing.payment` / `receipt` no cliente | Gap menor (rota exige view; API exige payment) |

**Nota:** com `billing.create`/`edit`, a Receção pode criar/editar campos **não-preço** do catálogo via API; a UI de Serviços esconde edição de preço. Risco baixo vs alterar preço oficial (já bloqueado).

---

## 14. UX (rótulos) — sem redesign

**Bons:** Preço oficial, Valor cobrado, Redução, Total a cobrar, Pago, Saldo (criação); aviso de catálogo intacto.

**Fracos:**

- Métodos de pagamento em enum (`DINHEIRO`…);
- Detalhe: «Pendente» em vez de «Saldo»;
- Histórico: «ID do paciente»;
- ORIGINAL pouco marcado no recibo;
- Lista de faturas sem pesquisa.

Não redesenhar nesta tarefa.

---

## 15. Decisão

**Classificação:** **ESSENCIAL** para a Receção (dinheiro + recibo + gate do Atendimento rápido).

| Pergunta | Resposta |
|---|---|
| Fluxo pronto para piloto? | **Quase** — operacional no happy path Atendimento → fatura → pagar → recibo |
| Precisa pequenos ajustes? | **SIM** (pesquisa/filtros mínimos, cancel UI, labels, deep-link serviço) |
| Tem risco financeiro? | **SIM, moderado** (overpay API; sem anular pagamento; cancel só API; lista fraca de saldos) |
| Duplicação com Atendimento rápido? | **SIM, parcial** (serviço não pré-seleccionado; paciente re-editável) |
| Faltam acções importantes? | **SIM** — UI cancelar fatura; lista saldos pendentes; filtros na lista |

---

## 16. Não feito (conforme pedido)

Sem Financeiro novo, Contabilidade, stock, catálogo, migração histórica, POS, despesas, lucro, redesign de dashboard, alteração de regras de redução/pagamento/recibo.

---

## 17. Alterações recomendadas (próxima tarefa — não desta auditoria)

Prioridade sugerida (polimento operacional, sem arquitectura nova):

1. **Pesquisa/filtro mínimo** na lista de faturas (paciente, estado, hoje) — reutilizar filtros API existentes onde possível.
2. **UI «Cancelar fatura»** com motivo, só se não `PAGA`, reutilizando `POST .../cancel/`.
3. **Deep-link Atendimento:** consumir `tipo=` para sugerir/pré-seleccionar serviço CONSULTA/CONTROLE (sem forçar).
4. **Labels:** Saldo no detalhe; métodos de pagamento em PT; ORIGINAL no recibo.
5. **Lista saldos pendentes** mínima (faturas `PENDENTE`/`PARCIAL`) ou deep-link do resumo — sem módulo financeiro.
6. **Guard de overpay** no `registar_pagamento` (não aceitar valor > saldo).
7. Tab Paciente → histórico com `patient id` preenchido.

**Fora de âmbito imediato:** anulação/reembolso de pagamento (precisa regra de negócio explícita + auditoria).

---

## 18. Matriz rápida SIM/NÃO

| Capacidade | |
|---|---|
| Criação de fatura | **SIM** |
| Redução | **SIM** |
| Pagamento integral | **SIM** |
| Pagamento parcial | **SIM** |
| Segundo pagamento | **SIM** |
| Saldo correcto (sobre cobrado) | **SIM** |
| Recibo | **SIM** |
| Segunda via | **SIM** |
| Cancelamento UI | **NÃO** (API SIM) |
| Anulação pagamento UI | **NÃO** |
| Pesquisa/filtros lista | **NÃO** (insuficiente) |
| Saldos pendentes (lista) | **NÃO** |
| Integração Atendimento rápido | **SIM** (deep-link; serviço não pré-preenchido) |
| Integração Marcações | **NÃO** (operacional) |

---

**Estado final:** `BILLING_AUDIT_COMPLETE`
