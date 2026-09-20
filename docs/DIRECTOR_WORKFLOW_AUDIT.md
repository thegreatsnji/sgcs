# Auditoria operacional — perfil DIRECTOR (SGCS SauVida)

**Data auditoria:** 2026-08-24  
**Hardening:** Sprint 27 (`docs/SPRINT27_DIRECTOR_WORKFLOW_HARDENING.md`) — 2026-08-25  
**Base operacional:** Receção `RECEPTION_READY_FOR_UAT` · Médico `DOCTOR_READY_FOR_UAT` · Laboratório `LABORATORY_READY_FOR_UAT` · Enfermagem `NURSING_READY_FOR_UAT`  
**Estado auditoria:** `DIRECTOR_WORKFLOW_AUDIT_COMPLETE`  
**Estado pós-hardening:** `DIRECTOR_READY_FOR_UAT`  
**UAT:** `docs/UAT_DIRECTOR_FINAL.md`

### Estado pós-Sprint 27 (resumo)

| Achado P0/P1 | Resolução |
|---|---|
| Dashboard dependia de `reception.view` | `GET /dashboard/director/` + FE dedicado |
| «Receita» ≠ faturado | KPIs Faturado / Recebido via `get_resumo_operacional` |
| Saldo = contagem | Saldo monetário FCFA + `faturas_com_saldo` secundário |
| PARCIAL omitido | Incluído na regra do resumo operacional |
| Capacidades clínicas/caixa excessivas | Seed DIRECTOR reduzido; 403 no backend |
| Lucro/despesas no home | Removidos do painel executivo do piloto |
| Serviços «mais vendidos» | Relabel «Serviços faturados» |
| Menu com 403 | Nav supervisão apenas |

---

**Âmbito original da auditoria:** leitura. Sem redesenho, sem módulo novo.  
**Nota:** o texto abaixo documenta o estado **antes** do hardening; usar a tabela acima e o Sprint 27 como fonte de verdade actual.

Código auditado em `C:\PROJECTS\SGCS` (backend Django + frontend React).

---

## Pergunta central

> O Director da Clínica SauVida consegue perceber rapidamente o estado operacional e financeiro da clínica sem assumir tarefas da Receção ou dos profissionais clínicos?

**Resposta (após Sprint 27):** **Sim, para o âmbito do piloto** — painel de supervisão com métricas financeiras/operacionais agregadas, sem operações de balcão nem edição clínica.

**Resposta (auditoria 2026-08-24):** **Ainda não, de forma fiável e isolada.**

O perfil **via** faturação, pagamentos, stock (leitura), relatórios e um painel executivo rico. Porém:

1. o **home** `/dashboard/director` **dependia de um endpoint da Receção** que o DIRECTOR **não tinha** (`reception.view`) — risco de **skeleton infinito**;
2. os rótulos financeiros **não correspondiam** aos cálculos (Receita ≠ faturado; Saldo ≠ montante em dívida);
3. o seed concedia **poder clínico e de balcão** (prescrever, iniciar consulta, criar fatura, receber pagamento);
4. o resumo correcto FATURADO / RECEBIDO / SALDO / REDUÇÃO **já existia** para a Receção e **não estava** no painel do Director.

Não se inventam KPIs. Não se mistura histórico migrado (`PatientHistory`) com `Fatura`/`Pagamento` nos agregados actuais — esse isolamento **já está** no resumo operacional da Receção e nos modelos de billing.

---

## 1. Papel do Director — capacidades actuais

Fonte: `seed_rbac.py` (`UserRole.DIRECTOR`) + rotas FE + permissões de acção.

| Capacidade | Classificação | Evidência |
|---|---|---|
| Ver painel executivo | **ESSENCIAL** (partido) | `/dashboard/director` — bloqueado se `/dashboard/reception/` devolver 403 |
| Ver recebido hoje/mês | **ESSENCIAL** | `BillingService.get_dashboard_summary` — rotulado «Receita» |
| Ver faturado vs recebido vs saldo vs redução | **AUSENTE** no painel Director; **ESSENCIAL** no produto | Existe em `GET /billing/resumo-operacional/` (`billing.view`); UI só na Receção |
| Ver dívida em dinheiro | **AUSENTE** no painel | Card «Saldo em dívida» = **contagem** de faturas `PENDENTE` |
| Supervisão de reduções | **ÚTIL** / descoberta fraca | API `RelatorioReducoesView` + `/billing/reducoes/pendentes`; não está no sub-nav de faturação |
| Pacientes atendidos hoje | **ESSENCIAL** | Vem do dashboard Receção (`attended_today` = check-ins **concluídos**) |
| Pessoas em espera | **ESSENCIAL** | Idem — `patients_waiting` |
| Consultas hoje / concluídas | **ESSENCIAL** | `appointments` dashboard (`consultation_date=hoje`) |
| Volume laboratorial | **ÚTIL** | Pedidos pendentes + em processamento; **sem** «aguarda regularização» |
| Stock baixo / sem stock | **ÚTIL** | Dashboard stock; **sem** expirados / próximos da validade no painel Director |
| Relatórios com período | **ÚTIL** | `/reports/*` hoje/semana/mês/ano |
| Exportar relatórios PDF/Excel/CSV | **ÚTIL** | `reports.export` — agregados flatten |
| Aprovar reduções especiais | **ÚTIL** | Role DIRECTOR em `reduction_service` |
| Ver catálogo / preços | **ÚTIL** | `billing.view`; **não** altera preço (`user_pode_alterar_preco` = só Admin) |
| Stock leitura | **ESSENCIAL** | `stock.view` + `pharmacy.view` + `stock.history` |
| Entrada/Saída/Ajuste/Perda stock | **INDEVIDA** (bloqueada) | Sem `stock.entry/exit/adjust`; UI esconde botões |
| Criar fatura / receber pagamento / cancelar | **INDEVIDA** | `billing.create`, `billing.payment`, `billing.edit` (cancel) |
| Triagem / fila / assign médico | **INDEVIDA** (bloqueada API Receção) | Sem `reception.*` |
| Iniciar/concluir consulta | **INDEVIDA** | `appointments.start/finish` |
| Diagnóstico / SOAP / prescrição | **INDEVIDA** | `appointments.clinical/diagnosis`, `doctors.prescription` |
| Validar resultado lab | **INDEVIDA** (bloqueada) | Sem `laboratory.results.validate` |
| Ver valores clínicos de resultados | **DESNECESSÁRIO** / **RISCO** | `laboratory.results.view` + `download` |
| Ver PatientHistory clínico completo | **ACEITÁVEL** com risco | Tem `appointments.clinical` → **não** é redigido |
| Gerir utilizadores / settings | **INDEVIDA** (ausente) | Sem `users.*`, `settings.*` — fronteira correcta vs Admin |
| Abrir caixa / despesas / «lucro» | **SECUNDÁRIA** / risco de KPI | Módulo `finance.*` completo; despesas **não** alimentadas no seed demo |
| Editar paciente | **INDEVIDA** | `patients.edit` (+ `create`, `export`, `print`) |
| Enviar notificações | **SECUNDÁRIA** | `notifications.send` / template / settings |

---

## 2. Dashboard `/dashboard/director`

**Página:** `DirectorRoleDashboardPage.tsx`  
**Home do perfil:** `getRoleDashboardPath(DIRECTOR)` → `/dashboard/director`

### Pedidos ao abrir (8–9)

| # | Query key | Endpoint | Permissão exigida | DIRECTOR tem? |
|---|---|---|---|---|
| 1 | `executive-dashboard` | reports executive | `reports.dashboard` | Sim |
| 2 | `reception-dashboard` | `GET /dashboard/reception/` | **`reception.view`** | **Não** |
| 3 | `consultas-dashboard` | appointments dashboard | `appointments.view` | Sim |
| 4 | `laboratory-dashboard` | laboratory dashboard | `laboratory.view` | Sim |
| 5 | `billing-dashboard` | billing dashboard | `billing.view` | Sim |
| 6 | `finance-dashboard` | finance dashboard | `finance.dashboard` | Sim |
| 7 | `notifications-dashboard` | notifications KPIs | `notifications.view` | Sim |
| 8 | `notifications-unread` | unread | `notifications.view` | Sim |
| 9 | `stock-urgencia-dash` | stock dashboard | `stock.view` / `pharmacy.view` | Sim (`retry: false`) |

**Risco P0:** `loading` exige `reception.data`. Sem `reception.view` o GET falha (403), `data` fica vazio, a condição `!reception.data` mantém o **skeleton para sempre**. O `isError` só é lido para o pedido **executive**. O mesmo padrão está em `/reports/executive`.

Stock é o único bloco que **não** bloqueia o loading (`stock.data ? …`).

### KPIs / cards / gráficos

| KPI | Fonte | Período | Útil | Risco |
|---|---|---|---|---|
| Pacientes Hoje | Receção `cards.attended_today` | Hoje; **check-ins COMPLETED** (não «entraram hoje») | Sim, se a API carregar | **P0** se 403; semântica incompleta |
| «N em espera» (badge) | Receção `patients_waiting` | Agora (WAITING+CALLED) | Sim | Idem P0 |
| Receita Hoje | `Pagamento` CONFIRMADO `Sum(valor)` `data_pagamento=hoje` | Hoje | Sim como **recebido** | Label **Receita** = recebido. **P0 copy/cálculo** |
| Consultas Hoje | `Appointment.consultation_date=hoje` | Hoje | Sim | Conta agendadas, não só realizadas |
| Consultas concluídas (badge) | status `CONCLUIDA` no mesmo QS | Hoje | Sim | — |
| Pedidos Laboratório | consultas: `pedidos_laboratorio_emitidos` **ou** lab pendentes+em processamento | Mistura hoje vs stock actual | Parcial | Duas fontes; fácil divergir |
| Lab pendentes (badge) | `resultados_pendentes` **ou** `pedidos_pendentes` | Agora | Parcial | «Pendentes» ≠ aguarda regularização ≠ aguarda validação |
| Taxa de Cobrança | `faturas_pagas / (pagas+pendentes)` **contagens all-time** | Sem período | Fraco | **Não é taxa do dia/mês**; ignora PARCIAL; não é dinheiro. **P1** |
| Receita do mês | Pagamentos confirmados desde dia 1 | Mês civil | Sim como **recebido** | Mesmo erro de label |
| Saldo em dívida | `Fatura.estado=PENDENTE`.count() | All-time | Não como saldo | **Contagem**, ignora `PARCIAL`. **P0** |
| Pagamentos hoje | COUNT pagamentos confirmados hoje | Hoje | Sim (volume) | No *billing* dashboard o mesmo campo é formatado como **moeda** (`formatCurrency`) — bug noutro ecrã |
| Exames (lab.) | pendentes + em processamento | Agora | Útil | Sem regularização |
| Stock baixo / Sem stock | `StockDashboardView` com precedência Sprint 26 | Agora | Sim | **Faltam** expirados e próximos da validade |
| Serviços mais utilizados | `ItemFatura` `Sum(quantidade)` top 5 | **All-time**, sem excluir canceladas de forma explícita | Parcial | Título FE «utilizados»; API «vendidos»; inclui linhas **não pagas**. **P1** semântica |
| Tendência de Receita (gráfico) | `MovimentoFinanceiro` ENTRADA, 30 dias | 30 dias | Fraco | **Não é** a série de `Pagamento`. Pode divergir da «Receita Hoje». **P1** |
| Crescimento de Pacientes | novos pacientes / dia (série) | 30 dias | Útil | — |
| Tendência de Consultas | série consultas | 30 dias | Útil | — |
| Actividade Laboratorial | série pedidos | 30 dias | Útil | Sem regularização |
| Alertas: resultados lab pendentes | count resultados EM_PROCESSAMENTO / RESULTADO_PENDENTE | Agora | Parcial | Link `/laboratory/results` (valores clínicos) |
| Alertas: faturas por liquidar | count PENDENTE | All-time | Parcial | Link lista faturas; não é montante |
| Alertas: notificações sistema | unread + falhas | Agora | Secundário | Ruído operacional de e-mail/SMS |
| Desempenho Receção | attended_today + espera | Hoje | Útil | Link **`/reception`** — RoleGuard **bloqueia** Director. **P1** |
| Desempenho Médico | concluídas / do dia | Hoje | Útil | Progresso «% concluídas» |
| Desempenho Lab | em_processamento | Agora | Fraco | KPI principal = em processamento, não volume do dia |
| Desempenho Faturação | «receita» hoje + taxa cobrança | Mistura | Parcial | Recicla erros de receita/taxa |
| Desempenho Financeiro | `finance.indicadores.lucro` | Mês caixa | **Enganoso** | «Margem operacional» = entradas caixa − saídas caixa. **P1** |

**Histórico migrado nos KPIs acima:** queries a `Fatura` / `Pagamento` / `Appointment` / `PedidoLaboratorial` / `ItemFatura` / `MovimentoFinanceiro` / stock. `PatientHistory` **não** entra. Ver §5.

**Duplicação:** `/dashboard/director` ≈ `/reports/executive` (mesmos componentes + mesmo bloqueio Receção). Billing e Finance repetem «receita» com **definições diferentes**.

---

## 3. Finanças — o que o Director consegue ver

| Pergunta | No painel Director | Noutro sítio acessível | Notas |
|---|---|---|---|
| Faturado hoje | **Não** | `resumo-operacional?periodo=hoje` (`billing.view`) — UI na Receção | `SUM(Fatura.total)` emitidas no período, excl. CANCELADA |
| Recebido hoje | **Sim**, com label «Receita Hoje» | Resumo operacional `total_recebido` | Pagamentos CONFIRMADO por `data_pagamento` |
| Recebido no mês | **Sim**, «Receita do mês» | Resumo `periodo=mes` | Idem |
| Saldo pendente (dinheiro) | **Não** (mostra contagem PENDENTE) | Resumo `saldo_pendente` | Soma `max(total − pago_confirmado, 0)` das faturas **emitidas no período** (não é dívida global da clínica) |
| Reduções | **Não** no dashboard | API relatório reduções; pendentes em `/billing/reducoes/pendentes` | `SUM(ItemFatura.valor_reducao)` no resumo operacional |
| Nº pagamentos | **Sim** (hoje, count) | Resumo `numero_pagamentos` | — |
| Faturas pagas / parciais | Pagas = count **all-time**; parciais **ausentes** | Lista faturas `estado` / `com_saldo` | PARCIAL existe no modelo |

### Conceitos (não misturar)

| Termo | Cálculo correcto no SGCS | Onde está bem separado |
|---|---|---|
| **FATURADO** | Soma de `Fatura.total` emitidas no período, excl. canceladas | `resumo_operacional.py` |
| **RECEBIDO** | Soma de `Pagamento.valor` CONFIRMADO com `data_pagamento` no período | Resumo + dashboard billing (`receita_*`) |
| **SALDO** | Dívida residual `total − pago_confirmado` | Resumo (por período de **emissão**); serializer fatura `saldo` |
| **REDUÇÃO** | `ItemFatura.valor_reducao` (preço oficial vs cobrado) | Resumo + `RelatorioReducoesView` |

O painel Director **colapsa** recebido sob o nome Receita e saldo sob uma **contagem**.

---

## 4. Filtro de período

| Superfície | Hoje | Semana | Mês | Personalizado |
|---|---|---|---|---|
| `/dashboard/director` | Implícito em alguns cards | **Não** | Implícito «receita mês» | **Não** |
| `/reports/*` (exceto executivo) | Sim (`ReportFilter`) | Sim | Sim (defeito) | Botão existe; **sem date pickers** — cai no **mês** (`resolve_date_range`) |
| `/billing/resumo-operacional/` | Sim | Sim | Sim | Sim (`data_inicio`/`data_fim`) — UI Receção |
| Relatório reduções API | `de` / `ate` | — | — | Query params; **sem** ecrã Director dedicado |

**Não criar nesta auditoria.** O filtro útil já existe no resumo operacional e nos reports.

---

## 5. Histórico migrado (CRÍTICO)

| Afirmação | Estado |
|---|---|
| PatientHistory financeiro **não** cria `Fatura` / `Pagamento` | **Confirmado** (Sprint 21 Fase 4 / testes `test_historico_migrado_excluido`) |
| Não aumenta receita/recebido dos KPIs billing | **Sim** — KPIs lêem `Pagamento` |
| Não cria dívida em `Fatura.saldo` | **Sim** — sem fatura migrada |
| Não entra no caixa actual | **Sim** — `MovimentoFinanceiro` nasce de pagamentos SGCS (`processar_pagamento_billing`), não de PatientHistory |
| Não contamina `resumo_operacional` | **Sim** — docstring + teste explícito |
| Dashboard Director | Mesmas tabelas billing/finance/appointments — **não** lê PatientHistory |

**Risco residual:** se no futuro alguém materializar Excel histórico em `Fatura`, os KPIs passam a incluí-lo. Hoje **não** é o caso. Eventos PatientHistory **clínicos** são visíveis ao Director (tem `appointments.clinical`) — risco de privacidade, não financeiro.

---

## 6. Receita — cálculo exacto

**Dashboard billing / cards Director «Receita Hoje / Mês»:**

```text
SUM(Pagamento.valor)
WHERE estado = CONFIRMADO
  AND data_pagamento::date = hoje   -- ou >= 1.º dia do mês
```

- **Não** é soma de faturas.
- **Não** é líquido de reduções (a redução já está no total da fatura; o pagamento é o cobrado).
- **É recebido (caixa operacional de faturação).**

**Finance `receita_hoje/mês` / gráfico «Tendência de Receita»:**

```text
SUM(MovimentoFinanceiro.valor) WHERE tipo = ENTRADA [data no período]
```

Pagamento confirmado **tenta** criar movimento de caixa (`FinanceService.processar_pagamento_billing`, abre caixa se preciso). Em condições normais aproxima-se do recebido; **não é a mesma query**.

**Executive `indicadores.receita_mensal`:** `FinanceService.calcular_fluxo_caixa()["receitas_mes"]` — outra vez **caixa**, não `Pagamento`.

**P0/P1:** o label «Receita» no painel do dono da clínica **não** corresponde a faturado nem a um único conceito. Badge «Pagamentos confirmados» está mais correcto do que o título.

---

## 7. Dívida / saldo

«Quanto os pacientes ainda devem?»

| Abordagem | Existe? | Adequada ao Director |
|---|---|---|
| Soma global de saldos (PENDENTE+PARCIAL, excl. canceladas) | **Não** como KPI Director | Seria o agregado certo |
| Count `estado=PENDENTE` | **Sim** (card + alerta) | Enganoso |
| Resumo `saldo_pendente` **só faturas emitidas no período** | Sim, Receção | Responde «deste turno/mês», não «stock de dívida» |
| Lista faturas `?com_saldo=true` | Sim, `/billing/invoices` | Lista (Director tem `billing.view`) |

**Recomendação (não implementar agora):** agregado monetário global + atalho à lista; **sem** ecrã de cobrança no perfil Director.

Director **não deve** receber pagamentos; hoje **pode** (`billing.payment`).

---

## 8. Reduções

| Questão | Achado |
|---|---|
| Total | API `RelatorioReducoesView` (`billing.view`): `total_reduzido`, nº linhas, média % |
| Período | Query `de` / `ate` na emissão da fatura |
| Quem concedeu | `reduzido_por`; relatório filtra `rececionista` |
| Motivo / serviço | `motivo_reducao`, `servico` no item; página pendentes mostra serviço + motivo |
| No dashboard Director | **Ausente** |
| Sub-nav faturação | **Não lista** reduções pendentes (só URL directa / manual) |
| Alteração retroactiva | Itens de fatura emitida não recalculam preço de catálogo; redução é da **linha**. Autorização aprova/rejeita pedido pendente — Director **pode** decidir |
| Painel | Sem KPI de reduções do dia/mês |

Supervisão: **possível** via API e página pendentes; **não** está no primeiro ecrã.

---

## 9. Despesas / lucro

| Questão | Achado |
|---|---|
| Director tem `finance.*`? | **Sim** — view/create/edit/delete, cash, expense, report, dashboard |
| Dados confiáveis para contabilidade? | **Não.** «Lucro» = entradas caixa − saídas caixa do mês |
| Despesas usadas pela clínica? | Módulo existe; **seed_demo não cria Despesas**. Operação real da SauVida no piloto é **faturação de balcão**, não tesouraria completa |
| KPI enganoso | Card departamento «Financeiro» + `indicadores.lucro` + «Margem operacional» | **P1** |

Não apresentar lucro como contabilidade completa até a clínica alimentar despesas de forma sistemática.

---

## 10. Pacientes

| Métrica | Existe? | Onde |
|---|---|---|
| Atendidos hoje | Parcial (`attended_today` = check-in concluído) | Dashboard Receção (bloqueado) |
| Novos pacientes | Sim | Executive `pacientes_novos` (filtro reports, defeito **mês**) — **não** está nos cards do home Director |
| Activos | Relatório pacientes (demografia) | `/reports/patients` |
| Tendência | Gráfico 30 dias | Home Director |

`patients.edit` / `create` / `export` / `print`: **INDEVIDO** para o papel de supervisão. Export de lista: endpoint `ready: False` («em desenvolvimento») — risco baixo de dump agora; permissão **existe**.

---

## 11. Consultas

| Indicador | Existe? |
|---|---|
| Consultas hoje | Sim (`consultas_do_dia`) |
| Concluídas | Sim (hoje) |
| Em espera | Sim no dashboard consultas (`CONFIRMADA`/`EM_ESPERA`) — **não** no KPI strip Director |
| Por médico | Relatório consultas `por_medico`; executive `top_medicos` — **não** no home |
| Por serviço/especialidade | Não como KPI Director |
| Diagnóstico no dashboard | **Não** (correcto) |

Director **pode** abrir consulta e prontuário (rotas `appointments` + `appointments.clinical`).

---

## 12. Médicos

| Necessidade | Existe? |
|---|---|
| Médicos activos | `medicos_em_servico` = médicos com consulta **EM_CONSULTA** agora (não «quadro activo») |
| Consultas por médico | Reports + `top_medicos` no executive JSON — home não lista |
| Ranking competitivo | `top_medicos[:5]` no payload executive — **não** renderizado no `DirectorRoleDashboardPage` |

Não inventar ranking no UI. O payload já traz top 5 — P3 se alguém ligar o JSON.

---

## 13. Laboratório

| Necessidade | Painel Director | Módulo lab (`laboratory.view`) |
|---|---|---|
| Pedidos / em processamento | Soma no card | Dashboard lab |
| Concluídos hoje | Não no strip; no card departamento | `concluidos_hoje` |
| Aguarda validação | Alerta usa `resultados_pendentes` | Sim |
| Aguarda regularização | **Ausente** | Lista com `estado_faturacao` (Sprint 25) |
| Volume por período | Gráfico 30 dias; report `periodo` | Sim |
| Valores clínicos | Não no KPI | **Sim** em `/laboratory/results/:id` (`results.view`) |

Director **não** tem `receive/process/validate`. **Não** marca regularizado (falta `reception.edit` no AND do Sprint 26).

**Exposição indevida:** detalhe de resultado (conclusão/parâmetros) + download. Classificação: **DESNECESSÁRIO** para o dono no dia-a-dia; **RISCO** de mínimo privilégio.

---

## 14. Stock

Painel Director: só **stock baixo** e **sem stock** (após Sprint 26 a contagem respeita precedência EXPIRADO).

**Não mostra:** expirados, próximos da validade (existem no dashboard stock e no painel enfermeiro).

| Acção | Director seed | UI `/stock` | API |
|---|---|---|---|
| GET lista / dashboard / histórico | Sim | Sim | 200 |
| Entrada / Saída | Não | Botões `canMutate` falsos | 403 |
| Ajuste / Perda / stock inicial | Não | `canAdjust` falso | 403 |
| Novo item | Não | `canCreate` falso | 403 |

**Read-only: confirmado** (cenário D). Risco residual: se alguém atribuir `pharmacy.edit` ao grupo Direção, a UI abre escrita.

---

## 15. Serviços mais utilizados

- **Fonte:** `ItemFatura` agrupado por `servico__nome`, `Sum(quantidade)`, top 5, **sem filtro de período**, **sem exigir pagamento**.
- FE Director: «Serviços mais **utilizados**» — alinhado a quantidade de linhas, não a dinheiro recebido.
- API/billing types: `servicos_mais_vendidos`.
- Relatório faturação: `servicos_vendidos` no período do report, com `Sum(subtotal)` — melhor, mas inclui não pagos.

**Não corrigir agora.** Semântica honesta: **linhas faturadas (quantidade), histórico completo, inclui por liquidar.**

---

## 16. Relatórios (menu Director)

Sidebar: Relatórios → `/reports`.

| Relatório | Rota | Conteúdo | Duplica dashboard? |
|---|---|---|---|
| BI charts | `/reports` | 4 gráficos 30 dias | Sim (mesmas séries) |
| Pacientes | `/reports/patients` | Novos, demografia | Parcial |
| Consultas | `/reports/appointments` | Volume, médicos, tempos | Parcial |
| Laboratório | `/reports/laboratory` | Pedidos/resultados counts | Parcial |
| Faturação | `/reports/billing` | Counts faturas/pagamentos + serviços | Parcial; **não** replica resumo operacional em FCFA |
| Financeiro | `/reports/finance` | Receitas/despesas **caixa** + lucro | Sim + perigo lucro |
| Executivo | `/reports/executive` | Clone do home Director | **Duplicado exacto** |
| Reduções | — | Só API | Falta na lista |
| Stock | — | Não há report stock | Director usa `/stock` |

Exportação: botões PDF / Excel / CSV em cada relatório genérico (`reports.export`).

---

## 17. Exportação

| Canal | Formato | Dados | PII |
|---|---|---|---|
| Reports | PDF, XLSX, CSV reais (`ReportService.exportar`) | Flatten do JSON do relatório (listas até ~20 itens no PDF) | Agregados sobretudo; `por_medico` / nomes de serviço; **não** dump de SOAP. Relatório pacientes: sexo/cidade/nacionalidade agregados |
| Celery `gerar_pdf` | Stub | Não é o caminho da UI | — |
| `GET /patients/export/` | Declarado csv/xlsx | `ready: False` | Permissão existe; ficheiro ainda não sai |
| Lab `results.download` | Ficheiro de resultado | **Clínico** | Director tem a permissão |

Director **pode** exportar agregados. Download de resultado lab é o maior risco de PII clínico.

---

## 18. Mobile (auditoria estática 375 / 390 / 430 / tablet / desktop)

Sem redesign. Comportamento esperado pelo layout actual (`grid gap-4 sm:grid-cols-2 xl:grid-cols-5`, gráficos `h-48`, `main px-4`).

| Viewport | Cards | Números | Gráficos | Tabelas | Filtros | Navegação |
|---|---|---|---|---|---|---|
| 375–430 | 1 coluna; hero + 5 KPIs + 4 cards = **muito scroll** | `formatCompactCurrency` (1,5k FCFA) ajuda | 1 gráfico de cada vez; eixo Y apertado (`left: -16`) | Não há tabela no home; faturas noutro ecrã = scroll horizontal típico | **Sem filtros** no home | `AppShell`: sidebar `hidden lg:block`; **drawer** mobile + `TopHeader` menu |
| Tablet | 2 colunas KPIs | Legível | 2×2 gráficos | — | — | Sidebar ainda oculta até `lg` |
| Desktop | 5 KPIs + 4 cards + gráficos 3/4 + alertas | OK | Úteis se a série caixa = expectativa | — | — | Sidebar |

**Não há CSS específico do Director.** UAT presencial (`UAT_DIRECTOR_PRESENCIAL.md`) ainda **não executado** nesta auditoria.

---

## 19. Primeiro ecrã (telemóvel, antes de scroll excessivo)

Ordem actual:

1. Hero «Painel executivo» + CTAs **Relatório completo** e **Financeiro** (empurram para BI/tesouraria)
2. KPI 1: Pacientes Hoje  
3. KPI 2: Receita Hoje (= recebido)  
4. KPI 3: Consultas  
5. KPI 4: Lab  
6. KPI 5: Taxa de cobrança (enganosa)  
7. Só **depois**: Receita do mês, «Saldo em dívida» (contagem), pagamentos hoje, exames, stock, serviços, gráficos, departamentos

**Recebido mês** e **dívida** não estão above-the-fold no telemóvel. **Saldo pendente em FCFA** não existe.

---

## 20. Alertas

| Alerta | Existe no painel? | Suficiente? |
|---|---|---|
| Stock baixo / sem stock | Card (não «alerta») | Parcial — falta expirado |
| Exames aguardam regularização | **Não** | Falta |
| Pagamentos pendentes | Count faturas PENDENTE | Parcial |
| Resultados aguardam validação | Sim (count) | Parcial |
| Problemas operacionais | Notificações sistema / falhas envio | Ruído |

Não há motor novo de notificações. O dashboard **não** chega para a manhã do Director se o bloco Receção 403 ou se a dívida/reduções/lab-regularização faltam.

---

## 21. Acesso clínico (mínimo privilégio)

| Conteúdo | Acesso Director | Classificação |
|---|---|---|
| Diagnóstico individual | Sim (`appointments.clinical` + `diagnosis`) | **DESNECESSÁRIO** / **RISCO** |
| Notas / SOAP | Sim (GET e PATCH) | **RISCO** |
| Prescrições | Sim (`doctors.prescription` + rotas `/doctor/*`) | **RISCO** |
| Resultados lab (valores) | Sim (`results.view` + download) | **DESNECESSÁRIO** |
| PatientHistory clínico (incl. migrado) | Sim — **não redigido** | **ACEITÁVEL** só se a clínica quiser o dono a ler prontuário; senão **RISCO** |
| Identidade + volume operacional | Sim | **NECESSÁRIO** |

Não se assume que o proprietário precisa de prontuário completo. O seed **já lhe dá**.

---

## 22. Acesso operacional indevido

| Acção | Consegue? | Classificação |
|---|---|---|
| Criar fatura | Sim (`billing.create` + UI `/billing/invoices/new`) | **INDEVIDA** |
| Receber pagamento | Sim (`billing.payment`) | **INDEVIDA** |
| Cancelar fatura | Sim (`billing.edit` / cancel) | **INDEVIDA** |
| Triagem | Não (sem `reception.create`) | Correcto |
| Atribuir médico / fila | Não (sem `reception.edit`; UI `/reception` bloqueada) | Correcto |
| Iniciar consulta | Sim (`appointments.start`) | **INDEVIDA** |
| Validar laboratório | Não | Correcto |
| Movimentar stock | Não | Correcto |
| Regularizar exame lab | Não (AND `reception.edit`+`billing.edit`) | Correcto |
| Abrir caixa / lançar despesa | Sim | **SECUNDÁRIO** / tesouraria |

O manual de formação pede *«sem operar atendimento»*; o RBAC **não** cumpre isso na faturação nem no clínico.

---

## 23. Administração vs Director

| | DIRECTOR (clínica) | ADMINISTRADOR (sistema) |
|---|---|---|
| Utilizadores / RBAC / audit / backups / flags | **Não** | Sim |
| Settings clínica / e-mail / segurança | **Não** | Sim |
| Preço oficial do catálogo | Vê; **não altera** | Altera (`user_pode_alterar_preco`) |
| Faturação operacional | **Sim (demasiado)** | Sim |
| Financeiro / caixas | **Sim** | Sim |
| Prontuário / prescrição | **Sim (demasiado)** | Superuser bypass |

Fronteira **settings/users** está correcta. Fronteira **clínica vs balcão vs médico** está **errada** no seed.

---

## 24. Preços

Regra anterior **mantida no código:** só `ADMINISTRADOR` / superuser altera `Servico.preco`. Teste `test_director_nao_altera_preco` → 400.

Director vê catálogo e preços (`billing.view`). **Não mudar.**

---

## 25. Stock read-only

Confirmado: GET sim; POST entrada/saída/ajuste/perda **não**. Ver §14.

---

## 26. Copy (não corrigir agora)

| Achado | Onde |
|---|---|
| «Receita» = recebido | KPI strip |
| «Saldo em dívida» = nº faturas PENDENTE | Card |
| «Taxa de Cobrança» = rácio de counts all-time | KPI |
| «Lucro» / «Margem operacional» | Departamento Financeiro |
| «Serviços mais utilizados» vs API vendidos | Home |
| «Relatórios e BI» | `/reports` |
| «Ver módulo →» | Department cards |
| «Novo pico» / «% vs. dia anterior» | Tendência de gráficos |
| Mix inglês em código (`collectionRate`) não no UI | — |
| Datas de gráficos `DD/MM` | `formatChartDate` |
| Hero empurra «Financeiro» (tesouraria) | Home |
| Billing cards: pagamentos hoje como **moeda** | `/billing` (não o card Director) |

Enums crus: não no home Director. Histórico stock (se abrir `/stock`) já humanizado na Sprint 26.

---

## 27. Gráficos — que decisão?

| Gráfico | Decisão clara? | Prioridade |
|---|---|---|
| Tendência de Receita (caixa 30d) | Só se a tesouraria estiver alinhada; senão confunde com recebido | **P2** (ou alinhar fonte) |
| Crescimento de Pacientes | «Estamos a registar mais utentes?» | Útil **P2** |
| Tendência de Consultas | Volume clínico | Útil **P2** |
| Actividade Laboratorial | Volume lab | Útil **P2** |
| Quatro gráficos no telemóvel | Pouca decisão por pixel | **P3** reduzir no primeiro ecrã |

Não manter gráfico só por parecer dashboard — o de receita é o mais perigoso pela fonte errada.

---

## 28. Performance

- **8–9 requests** em paralelo no home; `refetchInterval` 120s (executive) + 60s (unread).
- Loading **serial na prática**: espera **todos** os payloads (excepto stock).
- Dashboard Receção: loop Python para tempo médio de espera (N+1 conceptual) — irrelevante se 403.
- Finance e executive usam **cache**; billing dashboard **não**.
- Mobile: payload de 4 séries Recharts + 5 department cards.

Não optimizar sem evidência de campo; o bloqueio 403 é primeiro.

---

## 29. Cenário A — manhã (telemóvel 10h)

| Precisa | Consegue? | Cliques / scroll |
|---|---|---|
| Pacientes atendidos | Só se Receção API 200; e é «concluídos» | 0 se o painel abrir; senão **0 informação** |
| Pessoas em espera | Idem | Badge no 1.º KPI |
| Recebido hoje | Sim (se passar o loading) | 2.º card |
| Situação pagamentos | Count hoje; dívida = count PENDENTE | Scroll 1 ecrã |
| Stock crítico | Só baixo/sem; sem expirados | Scroll 2+ ecrãs |

**Fricção:** se P0 loading, **zero** resposta. Se abrir: ~2–3 ecrãs de scroll; hero não responde à pergunta.

---

## 30. Cenário B — fim do dia

| Pergunta | Resposta no painel Director |
|---|---|
| Quanto faturámos? | **Não** |
| Quanto recebemos? | Sim (labels «Receita») |
| Quanto ficou pendente? | **Não** em FCFA |
| Quanto foi reduzido? | **Não** |
| Quantos pacientes? | Parcial (concluídos) / 403 |
| Quantas consultas? | Sim |
| Quantos exames? | Parcial (fila actual, não «hoje concluídos» no strip) |

O **resumo operacional da Receção** responde faturado/recebido/saldo/reduções/nº pagamentos. O Director **não o vê na UI**.

---

## 31. Cenário C — mês

| Pedido | Home Director | Reports |
|---|---|---|
| Recebido | Card mês (pagamentos) | Finance/billing reports (definições diferentes) |
| Faturado | Não | Report billing = **counts**, não FCFA total |
| Dívida | Count PENDENTE all-time | Não |
| Reduções | Não | API apenas |
| Serviços mais usados | All-time quantidade | Report billing no período |
| Volume pacientes | Gráfico 30d; novos no JSON executive | `/reports/patients` com filtro mês |

Seleccionar mês no **home: impossível**. Em reports: sim, excepto executivo (clone sem filtro).

---

## 32. Cenário D — stock

Ceftriaxona stock baixo: Director **vê** o número no card (e a lista em `/stock` read-only). **Não** altera quantidade. Enfermeiro **sim** (Sprint 26). **Confirmado.**

---

## 33. Cenário E — lab

Agregado operacional: pendentes + processamento + alerta de resultados. **Não** há count «aguarda regularização». Abrir detalhe de resultado mostra **valores**. Para o dono, o agregado da lista lab com badge de regularização (Sprint 25) seria suficiente — hoje o atalho do alerta vai a **resultados**, não à fila operacional.

---

## 34. Cenário F — privacidade (documentar, não corrigir)

Tentativa Director:

| Alvo | Resultado actual |
|---|---|
| Diagnóstico / SOAP | Aberto (prontuário) |
| Notas médicas | PATCH possível |
| Laboratório detalhado | GET + download |
| PatientHistory clínico | Texto completo (não redigido) |

---

## 35. RBAC — tabela DIRECTOR

Permissões seed (`DEFAULT_ROLE_PERMISSIONS[DIRECTOR]`):

| Permissão | Classificação |
|---|---|
| `patients.view` | CORRECTA |
| `patients.create` | DESNECESSÁRIA |
| `patients.edit` | RISCO |
| `patients.export` | RISCO (ficheiro ainda stub) |
| `patients.print` | DESNECESSÁRIA |
| `appointments.view` | CORRECTA |
| `appointments.create` | DESNECESSÁRIA |
| `appointments.edit` | RISCO |
| `appointments.confirm` | DESNECESSÁRIA |
| `appointments.start` | RISCO |
| `appointments.finish` | RISCO |
| `appointments.cancel` | DESNECESSÁRIA |
| `appointments.clinical` | RISCO |
| `appointments.diagnosis` | RISCO |
| `appointments.request_lab` | DESNECESSÁRIA |
| `appointments.request_imaging` | DESNECESSÁRIA |
| `appointments.followup` | DESNECESSÁRIA |
| `doctors.view` | CORRECTA / ÚTIL |
| `doctors.prescription` | RISCO |
| `doctors.treatment` / `evolution` / `discharge` / `followup` | RISCO |
| `laboratory.view` | CORRECTA (agregado) |
| `laboratory.results.view` | RISCO (valores) |
| `laboratory.results.download` | RISCO |
| `billing.view` | CORRECTA |
| `billing.create` | RISCO |
| `billing.edit` | RISCO (cancelar fatura) |
| `billing.delete` | RISCO |
| `billing.export` | ÚTIL / revisar PII |
| `billing.payment` | RISCO |
| `billing.receipt` | ACEITÁVEL leitura; tem a perm de recibo |
| `billing.quote` | DESNECESSÁRIA |
| `finance.view` | ACEITÁVEL com caveat lucro |
| `finance.create` / `edit` / `delete` | RISCO / tesouraria |
| `finance.cash` | RISCO |
| `finance.expense` | DESNECESSÁRIA até a clínica usar |
| `finance.report` / `finance.dashboard` | ACEITÁVEL se copy for honesta |
| `reports.view` / `export` / `dashboard` / `statistics` | CORRECTA |
| `dashboard.view` | CORRECTA |
| `pharmacy.view` | CORRECTA |
| `stock.view` / `stock.history` | CORRECTA |
| `notifications.view` | ACEITÁVEL |
| `notifications.send` / `template` / `settings` / `history` | DESNECESSÁRIA |
| `reception.view` | **FALTANTE** para o KPI de espera **ou** o dashboard não deveria chamá-lo |
| `reception.*` resto | Correctamente ausente |
| `users.*` / `settings.*` | Correctamente ausente |
| `stock.entry/exit/adjust` | Correctamente ausente |
| `laboratory.results.validate` | Correctamente ausente |

---

## 36. Não fazer (auditoria — cumprido)

Não se criou BI novo, contabilidade, módulo financeiro, despesas, lucro extra, gráficos novos, alterações a Receção/Médico/Lab/Enfermagem/catálogo, notificações, IA, nem redesign do dashboard.

---

## 37. Prioridades

### P0 — integridade financeira, privacidade, segurança, painel inutilizável

1. Home Director **bloqueado** por `GET /dashboard/reception/` + `reception.view` em falta.  
2. «Receita» **é recebido** (pagamentos); não é faturado.  
3. «Saldo em dívida» **é contagem PENDENTE**, ignora PARCIAL, não é FCFA.  
4. RBAC: Director **prescreve, edita SOAP, inicia consulta, fatura e recebe** — contradiz o papel de supervisão.

### P1 — bloqueia piloto de direcção

1. Resumo FATURADO/RECEBIDO/SALDO/REDUÇÃO existe e **não está no ecrã Director**.  
2. Taxa de cobrança e serviços «vendidos» **all-time** / sem pagamento.  
3. Gráfico de receita = **caixa**, KPI = **pagamento**.  
4. «Lucro» / margem sem despesas operacionais reais.  
5. Links para `/reception` e «Exames lab.» na faturação **403/redirect**.  
6. Sem expirados/próximos da validade / sem regularização lab no painel.  
7. Primeiro ecrã mobile: hero + taxa inútil; mês e dívida lá em baixo.  
8. Reduções: supervisão possível mas **invisível** no dashboard/nav.

### P2 — melhoria importante

Copy (→, BI, Receita, Saldo); filtro período no home **reutilizando** resumo operacional; reduzir gráficos no telemóvel; `patients.edit`; notificações send; report billing em FCFA alinhado ao resumo; personalizado com datas.

### P3 — opcional

Clone `/reports/executive`; top médicos; export pacientes stub; ranking.

---

## 38. Recomendação

**Não** declarar UAT de Director.

**Próximo passo (quando autorizado):** sprint de **hardening** no perfil existente — como 24/25/26 — **sem** BI novo:

1. Desacoplar o home de `reception.view` **ou** expor só agregados de espera/atendidos num endpoint `dashboard.view` / `reports.dashboard`.  
2. Reutilizar `resumo_operacional` no primeiro ecrã (hoje/mês): recebido, faturado, saldo **em FCFA**, reduções.  
3. Corrigir labels; dívida monetária; não mostrar lucro.  
4. Cortar RBAC operacional/clínico ao mínimo (view financeiro + reports + stock read + aprovar reduções).  
5. Mobile: 4 números acima da dobra; gráficos abaixo.  
6. Validar presencialmente se o dono **quer** ler prontuário — default desta auditoria: **não**.

Workaround actual (não é UAT): abrir **Faturação** e **Relatórios** com espírito crítico nos rótulos; **não** usar o Director como rececionista nem como médico; **não** confiar no card «Saldo em dívida»; em bases já seedadas o **painel home pode nem abrir**.

---

## Fontes (código)

- `backend/apps/users/management/commands/seed_rbac.py`  
- `backend/apps/billing/services/billing_service.py` (`get_dashboard_summary`)  
- `backend/apps/billing/services/resumo_operacional.py`  
- `backend/apps/billing/services/catalog_service.py` (`user_pode_alterar_preco`)  
- `backend/apps/finance/services/finance_service.py` (`calcular_fluxo_caixa`)  
- `backend/apps/reports/services/dashboard_service.py`, `statistics_service.py`  
- `backend/apps/dashboard/views.py` (`ReceptionDashboardView` → `reception.view`)  
- `backend/apps/patients/privacy.py`  
- `frontend/src/pages/dashboards/DirectorRoleDashboardPage.tsx`  
- `frontend/src/features/reports/components/ExecutiveKpiStrip.tsx`, `ExecutiveChartsGrid.tsx`, `DepartmentPerformanceGrid.tsx`  
- `frontend/src/constants/navigation.ts`, `frontend/src/routes/index.tsx`  
- `docs/MANUAL_DIRECTOR.md`, `docs/FORMACAO_DIRECTOR.md`, `docs/UAT_DIRECTOR_PRESENCIAL.md`
