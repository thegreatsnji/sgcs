# Auditoria operacional — perfil LABORATÓRIO (SGCS SauVida)

**Data:** 2026-08-24  
**Base operacional:** Receção `RECEPTION_READY_FOR_UAT` · Médico `DOCTOR_READY_FOR_UAT`  
**Âmbito:** auditoria de leitura do fluxo **a partir do pedido no laboratório**. Sem redesenho, sem módulo novo, sem alteração de modelos/API/JWT/RBAC/billing/histórico.  
**Código:** estado actual inclui o hardening já merged (gate de regularização, identificação, pesquisa/filtros, impressão pós-validação). Esta ficha descreve o **comportamento real agora**, não um desenho futuro.  
**Estado:** `LABORATORY_WORKFLOW_AUDIT_COMPLETE`

---

## Pergunta central

> Um técnico de laboratório da Clínica SauVida consegue receber, processar, registar, validar e publicar um exame de forma simples, segura e rastreável?

**Resposta:** **Sim, no fluxo com consulta médica e regularização na Receção**, sujeito a UAT presencial.

O técnico vê o pedido, identifica o utente, pode receber/colher, **não inicia processamento** enquanto `AGUARDA_REGULARIZACAO`, regista resultado (texto e/ou parâmetros livres), valida com confirmação, e o médico vê valores só após validar. Há rastreio (actor, timestamps, audit).

**Limitações reais (não inventadas):**

- exame **sem consulta** (walk-in) **não existe** (`consulta` é FK obrigatória);
- **cancelar/rejeitar** pedido lab **não tem acção**;
- **publicar** ≠ disponibilizar ao médico (validar já disponibiliza; publicar = «entregue»);
- colheita é **opcional** e o estado `AGUARDANDO_COLHEITA` é semanticamente invertido (ver §7);
- parâmetros **não** vêm do catálogo.

---

## 1. Painel do laboratório

**Home do perfil:** `/dashboard/laboratory` — `LaboratoryRoleDashboardPage`  
**Painel operacional:** `/laboratory` — `LaboratoryDashboardPage` (sub-nav; **não** está no menu lateral)

**Menu LABORATORIO:** Painel · Pendentes · Colheitas · Resultados · Histórico · Notificações.  
**Falta no menu:** Processamento (`/laboratory/today`) e o painel `/laboratory` — só na sub-nav interna.

| Questão | Achado |
|---|---|
| Pedidos pendentes? | **Sim** — KPI + lista top 5 (número LAB + nome) + CTA |
| Em processamento? | **Sim** — KPI |
| Aguardam validação? | **No painel `/laboratory` e em Resultados.** **Não** no role dashboard |
| Concluídos? | **Sim** — «Concluídos hoje» (estado pedido `CONCLUIDO`, não necessariamente validado) |
| Resultados recentes? | **Sim** — módulo Resultados |
| Pacientes? | **Não** como lista; utente aparece no pedido |
| Filtros no painel? | **Não** (só KPIs) |
| Prioridades no painel? | **Não** |

KPI «Pendentes» conta `PENDENTE + RECEBIDO + AGUARDANDO_COLHEITA`, mas o badge diz «Aguardam receção» — copy **incorrecta**.

**“Que exames tenho de fazer agora?”:** **ACEITAVEL.** O caminho útil é **Pendentes**. O técnico não vê no primeiro ecrã: (a) só os que já estão regularizados vs a aguardar Receção; (b) resultados a validar.

---

## 2. Fila / lista de pedidos

**Tabelas:** `LaboratoryTable` (Pendentes, Processamento/hoje) · `CollectionQueue` (colheitas).

| Coluna | Presente |
|---|---|
| Nome do utente | Sim |
| Código do utente (`patient_number`) | Sim (lista) |
| Número do pedido (`LAB-…`) | Sim (mono) |
| Exame solicitado | Sim — `exames[].nome_exame` (nome humano) |
| Médico solicitante | Sim |
| Data/hora | Sim — formatada PT |
| Prioridade | Sim — rótulos PT (`PRIORITY_LABELS`) |
| Estado | Sim — `estado_operacional_label` (ex. «Aguarda validação») |
| Regularização | Sim — badge sem montantes |
| Acção principal | Receber / Colheita / Processar (bloqueado se não `pode_processar`) / Concluir processamento / Ver |

**Pesquisa (`q`):** ligada em **Pendentes** (utente, código, exame, número do pedido). **Não** na fila de colheitas nem em Processamento/hoje.

**Filtros (Pendentes):** estado, prioridade, data, regularização. **Não** filtro dedicado «exame» (coberto pela pesquisa).

---

## 3. Estados do pedido (backend reais)

Há **dois** eixos. Não misturar com estados inventados (`SOLICITADO`, `PUBLICADO` no pedido, etc.).

### 3.1 Pedido laboratorial (`PedidoLaboratorial.estado`)

| Valor persistido | Copy PT |
|---|---|
| `PENDENTE` | Pendente |
| `RECEBIDO` | Recebido |
| `AGUARDANDO_COLHEITA` | Aguardando colheita |
| `EM_PROCESSAMENTO` | Em processamento |
| `CONCLUIDO` | Processamento concluído (UI) / Concluído (modelo) |
| `CANCELADO` | Cancelado |

`AGUARDA_REGULARIZACAO` **não** é estado deste modelo — é `PedidoLaboratorio.estado_faturacao` (consulta).

### 3.2 Resultado (`ResultadoLaboratorial.estado`)

| Valor | Copy PT |
|---|---|
| `EM_PROCESSAMENTO` | Em processamento (pouco usado no create — o create já grava `RESULTADO_PENDENTE`) |
| `RESULTADO_PENDENTE` | Resultado pendente / «Aguarda validação» |
| `VALIDADO` | Validado |
| `ENTREGUE` | Entregue |

### 3.3 Pedido clínico na consulta (`PedidoLaboratorio.estado`)

`PENDENTE` · `EM_PROCESSAMENTO` · `CONCLUIDO` · `CANCELADO` — **só passa a CONCLUIDO na validação do resultado**, não em «Concluir processamento».

### 3.4 Matriz de transições do pedido lab

Transições inválidas: `validate_transicao` rejeita com mensagem «Não é possível {acção} neste estado».

| Estado actual | Acção | Próximo | Gate extra |
|---|---|---|---|
| PENDENTE | Receber | RECEBIDO | Não (regularização **não** bloqueia) |
| RECEBIDO | Registar colheita | AGUARDANDO_COLHEITA | Não |
| RECEBIDO | Iniciar processamento | EM_PROCESSAMENTO | **Sim** — não se `AGUARDA_REGULARIZACAO` |
| AGUARDANDO_COLHEITA | Registar colheita (de novo) | AGUARDANDO_COLHEITA | Não (repete timestamp) |
| AGUARDANDO_COLHEITA | Iniciar processamento | EM_PROCESSAMENTO | **Sim** — regularização |
| EM_PROCESSAMENTO | Concluir processamento | CONCLUIDO | Não |
| EM_PROCESSAMENTO ou CONCLUIDO | Criar resultado | (resultado `RESULTADO_PENDENTE`) | Pedido não muda até validar |
| RESULTADO_PENDENTE | Validar | pedido → CONCLUIDO se ainda não; resultado → VALIDADO | Papel LAB/Admin |
| VALIDADO | Marcar como entregue | resultado → ENTREGUE | — |
| CONCLUIDO / CANCELADO | Editar observações/prioridade | Bloqueado | — |

**Não há** transição de código para `CANCELADO` no serviço lab.

Colheita **não** é obrigatória: de `RECEBIDO` pode ir directo a processar.

---

## 4. Regularização / pagamento (crítico)

O médico cria `PedidoLaboratorio` com `estado_faturacao = AGUARDA_REGULARIZACAO` e o sistema cria o `PedidoLaboratorial` lab (`PENDENTE`).

| Questão | Comportamento real |
|---|---|
| Lab vê o pedido? | **Sim.** Permanece visível. Badge «Aguarda regularização». Banner no detalhe. |
| Pode receber? | **Sim.** |
| Pode registar colheita? | **Sim.** |
| Pode processar (`start`)? | **Não.** API 400: *«Este exame aguarda regularização na Receção.»* Botão Processar `disabled`. |
| Receção marca regularizado? | **Sim.** `POST /api/v1/reception/mark-lab-order-billed/{order_id}/` — `estado_faturacao → REGULARIZADO`. Idempotente (`already_regularized`). UI `/reception/lab-orders`. **Não cria pagamento.** |
| Estado final financeiro | `REGULARIZADO` (não muda o estado operacional do pedido lab). |
| Override / urgência bypass? | **Não.** Prioridade EMERGENCY **não** ignora o gate. |
| Montantes no lab? | **Não.** Só labels operacionais. |

**Risco de exame sem autorização:** o técnico **não** inicia processamento nem (por isso) cria resultado no caminho normal. **Pode** receber e colher amostra **antes** da regularização. Não é bypass do gate de análise; é trabalho de colheita pré-pagamento. Política da clínica: **não inventada** — documentar na UAT se isso é aceitável.

---

## 5. Pedido do catálogo

| Aspecto | Achado |
|---|---|
| Serviço estruturado | Opcional: `PedidoLaboratorio.servico` (categoria `LABORATORIO`) |
| Descrição / nome | `tipo_exame` — do catálogo (`servico.nome`) ou texto livre do médico |
| Texto livre | **Sim**, se o médico não escolher serviço |
| Múltiplos exames | **Vários pedidos** (um `PedidoLaboratorio` + um `PedidoLaboratorial` + um `ExameLaboratorial` por solicitação). Não é um único pedido com N linhas de catálogo no mesmo número LAB. |
| Label na lista lab | `nome_exame` humano. Código de serviço **não** é o título. Categoria do exame lab default `GERAL` (não herda hematologia/bioquímica do catálogo). |

---

## 6. Paciente correcto

No **detalhe do pedido** e no **registo/edição de resultado** (painel esquerdo persistente):

- nome, `patient_number`, sexo, idade/DN, número LAB, médico, exames.

**Risco residual:** criar resultado em `/laboratory/results/new` **sem** `?pedido=` mostra campo **«ID do pedido laboratorial»** (número interno). Caminho perigoso se usado. O fluxo normal (botão no pedido) traz o utente já identificado.

---

## 7. Colheita

| Questão | Achado |
|---|---|
| Existe? | **Sim** — botão «Colheita» / «Registar colheita»; `data_colheita`; audit `COLHEITA_REALIZADA` |
| Tipo de amostra? | **Não** |
| Responsável dedicado? | **Não** (actor = utilizador no audit) |
| Obrigatória? | **Não** — `start` aceita `RECEBIDO` |
| Semântica do estado | «Registar colheita» **passa o estado para `AGUARDANDO_COLHEITA`** com data de colheita já preenchida. O nome sugere espera; o acto é o registo. |

Se SauVida na prática colhe sem este clique, o fluxo **não bloqueia** (P2/P3 operacional). A copy/estado invertidos são **P2**.

---

## 8. Processamento

«Estou a trabalhar neste exame» = **Iniciar processamento**.

- timestamp: `updated_at` (não há `data_inicio` dedicada);
- actor: audit `EXAME_INICIADO`;
- estado: `EM_PROCESSAMENTO`;
- «Concluir processamento»: `CONCLUIDO` + `data_conclusao` — **só processamento técnico**, não «resultado validado».

Pode **saltar** concluir e ir a «Registar resultado» ainda em `EM_PROCESSAMENTO`.

---

## 9. Resultados — formulário

Campos: observações, conclusão, parâmetros (linhas livres: nome, valor, unidade, min, max, interpretação calculada), anexos (PDF/PNG/JPEG/DOCX) **depois** de existir resultado.

Nada é obrigatório excepto o pedido. Técnico **não** é forçado a preencher hemograma completo. Pode gravar só conclusão (ex. POSITIVO).

Anexo **não** no primeiro ecrã de create — só no detalhe enquanto editável.

---

## 10. Parâmetros

**Não vêm do catálogo. Não são pré-configurados por exame.** O técnico adiciona linhas. Unidade/referência opcionais. Interpretação: NORMAL/ALTO/BAIXO (API); UI também sugere CRÍTICO se valor > 1,2× máximo.

Não construir catálogo de parâmetros nesta auditoria.

---

## 11. Resultado textual

**Suportado.** `conclusao` / `observacoes` texto livre. Valor de parâmetro é `CharField` — aceita «Positivo» / «Negativo». Sem obrigação numérica.

---

## 12. Validação (ponto clínico crítico)

| Questão | Achado |
|---|---|
| Quem valida? | `LABORATORIO` (`laboratory.results.validate`) e Admin/superuser. **Médico não.** |
| Antes | Médico: lista de resultados filtrada a VALIDADO/ENTREGUE; no prontuário vê cartão **sem valores** (`disponivel: false`, «Aguarda validação»). |
| Depois | Valores no prontuário da **mesma consulta**; notificação assíncrona; histórico do utente (`HistoryEventType.EXAME`). Conclusão **anexa-se** a `consulta.clinical_notes`. |
| Confirmação UI | `window.confirm` com texto claro (disponível clinicamente; deixa de ser editável). |
| Actor / timestamp | `validado_por`, `data_validacao`, audit `RESULTADO_VALIDADO` |
| Revalidação | **Não** — só pendentes/em processamento do resultado |

---

## 13. Alteração após validação

**Não permitido.** `is_editavel` falso; serviço: *«Não é possível alterar um resultado já validado.»* Anexos e parâmetros também bloqueados.

Sem fluxo de invalidação/revisão. Correcção exigiria Admin/DB — **não existe** no produto. Risco residual: erro validado fica permanente (P2 processo, não P0 de edição silenciosa).

---

## 14. Publicação vs validação

| Acto | Efeito real |
|---|---|
| **Validar** | Disponível ao médico; imprimível; pedido clínico CONCLUIDO |
| **Marcar como entregue** (API `publish`) | `ENTREGUE` + `data_publicacao`. Médico **já** via o resultado. |

São **redundantes** para SauVida se «entregue» não tiver uso operacional (levantar papel, arquivo). UI já não diz «Publicar ao médico». KPI Resultados ainda diz «Prontos a publicar» / «Ao médico» no entregues — **fricção de copy (P2)**.

Impressão: a partir de VALIDADO, **sem** exigir ENTREGUE.

---

## 15. Médico (E2E)

```
Médico solicita (catálogo ou texto) + prioridade
  → PedidoLaboratorio AGUARDA_REGULARIZACAO + PedidoLaboratorial PENDENTE
Receção regulariza (marca; fatura à parte)
Lab: receber → [colheita opcional] → processar → registar → validar
Médico: tab Laboratório da consulta + /laboratory/results (só validados)
```

Não precisa de pesquisar o utente **se estiver na consulta certa**. Lista global de resultados do médico também existe (filtrada).

---

## 16. Receção

| Questão | Achado |
|---|---|
| Estado operacional lab? | Não a fila lab; sim a lista de **exames a regularizar** (nome exame, utente, label faturação) |
| Marca regularização? | Sim (sem ver valores clínicos do resultado) |
| Vê valores? | Sem `laboratory.results.view` no seed RECECIONISTA → 403 |
| Valida / edita resultado? | Não |

---

## 17. Impressão

`LabResultPrint` + `PrintDocument` (default **Clínica SauVida**). Só se VALIDADO/ENTREGUE.

Inclui: clínica, utente, código, sexo/idade, exame(s), resultado (parâmetros + unidades + referências se existirem), conclusão/obs., data, validador, número LAB, linha «Estado: Validado». Técnico (`responsavel_nome`) no corpo.

Logo: placeholder «LOGO» se não passar `clinicLogoUrl` (P3).

Não validado: botão Imprimir **ausente**.

---

## 18. Segunda impressão

`window.print()` no mesmo resultado. **Não** cria registo novo, **não** muda estado. Download de anexo gera audit `RESULTADO_DOWNLOAD`; **impressão de ecrã não** gera audit próprio (P3).

---

## 19. Cancelamento / rejeição

Estado `CANCELADO` existe no modelo. **Sem** endpoint/botão «cancelar», «amostra inválida» ou «não realizado». Pedidos errados ficam no fluxo até serem ignorados operacionalmente.

---

## 20. Exames directos (walk-in)

**Não suportado.** `PedidoLaboratorial.consulta` é `ForeignKey` obrigatória. Receção **não** cria pedido lab autónomo. Documentado; não implementar nesta auditoria.

---

## 21. Urgência / prioridade

Existe (`LOW/NORMAL/HIGH/EMERGENCY` da fila). Aparece no lab. Ordenação das listas pendentes/hoje/colheitas por `PRIORITY_ORDER` (emergência primeiro). **Não** bypassa regularização.

---

## 22. Histórico do paciente (vista LABORATORIO)

Seed: `patients.view` apenas. Sem `appointments.clinical`.

| Dado | Classificação |
|---|---|
| Identidade, código, sexo, idade | **NECESSÁRIO** |
| Alergias (leitura) | **ACEITÁVEL** (segurança de amostra) |
| Diagnóstico / SOAP / notas médicas | Redigido / 403 prontuário — **NECESSÁRIO** estar bloqueado |
| Ficha completa via «Ver ficha do paciente» | **ACEITÁVEL** com redacção; risco de curiosidade |
| Faturação / pagamentos | Sem `billing.*` — **correcto** |
| Histórico PatientHistory clínico | Descrição redigida — **ACEITÁVEL** |

---

## 23. Histórico migrado

Eventos `LABORATORIO` da migração tornam-se `PatientHistory` (`HistoryEventType.EXAME`), textual ou «alinhado», **read-only**. **Não** criam `ResultadoLaboratorial` nem entram na fila de validar/publicar.

---

## 24. Privacidade

| Recurso | LABORATORIO |
|---|---|
| Notas médicas / diagnóstico | Sem `appointments.clinical` |
| Faturação / pagamentos / receita | Sem `billing.*` |
| Stock de urgência | Sem `stock.*` / `pharmacy.*` |
| Editar ficha administrativa | Sem `patients.edit` |
| Ver resultado não validado | **Sim** (é a função) |
| Ver todos os resultados de todos os médicos | **Sim** (`listar_resultados` sem filtro por médico para LAB) — **ACEITÁVEL** operacional; não é isolamento por técnico |

---

## 25. RBAC

**Pode (seed):** ver/receber/colher/processar/concluir pedido; criar/editar/validar/publicar/descarregar resultados; `dashboard.view`; `notifications.view`; `patients.view`.

**Não pode:** `billing.*`, `appointments.clinical/diagnosis`, `doctors.prescription`, `users.*`, `settings.*`, `stock.*`.

`laboratory.edit` permite PATCH observações/prioridade do pedido (não catálogo de preços).

---

## 26. Copy

Globalmente PT. Problemas:

- KPI Pendentes «Aguardam receção» (inclui já recebidos);
- Resultados: «Prontos a publicar», «Ao médico» em entregues;
- `AGUARDANDO_COLHEITA` após colheita registada;
- «Pedido concluído» no toast de finish (só processamento);
- `← Voltar`; campo «ID do pedido»;
- enums na API (não na tabela principal);
- datas na UI formatadas (não ISO cruas nas listas).

Não corrigido nesta auditoria.

---

## 27. UX / fricção — fluxo principal

Abrir Pendentes → Ver pedido → identificar utente → Receber → (Colheita opcional) → Processar → Registar resultado (página nova) → Guardar → Validar (confirm) → Imprimir / Entregue.

| Métrica | Ordem de grandeza |
|---|---|
| Páginas | 4–5 (pendentes, detalhe, create resultado, detalhe resultado) |
| Cliques | ~8–12 no caminho feliz |
| Campos | Mínimos se só texto; muitos se preencher parâmetros à mão |
| Pesquisas repetidas | Evitáveis se seguir o pedido |

**Classificação:** **ACEITAVEL**. Não BLOQUEANTE. **MELHORAR:** publicar vs validar; estado de colheita; KPI do role dashboard sem «a validar»; campo ID cru.

---

## 28. Cenário A — Lab normal (Hemograma)

Pedido do catálogo + regularização + receber + processar + valores + validar + médico vê. Um resultado por pedido (`OneToOne`). Sem duplicar se o create for repetido (erro «Já existe um resultado»). **OK.**

---

## 29. Cenário B — Ainda não pago

Pedido visível. Processar recusado (API + botão). Receber/colher **permitidos**. Sem override.

---

## 30. Cenário C — Não validado

Médico: estado sem valores. Após validar: `disponivel: true` com parâmetros/conclusão.

---

## 31. Cenário D — Paciente errado

Identificação visível no fluxo ligado ao pedido. Risco maior: create por ID numérico; homónimos se o técnico não ler o código.

---

## 32. Cenário E — Múltiplos exames

Vários números LAB. Cada um com o seu estado e o seu resultado. Um não altera o outro. Lab vê todos na fila.

**Nota:** um «Hemograma + Glicemia» no mesmo acto médico = **dois** pedidos para o técnico, não um painel com dois parâmetros pré-carregados.

---

## 33. Cenário F — Positivo/Negativo

Conclusão ou valor textual do parâmetro. **OK.**

---

## 34. Cenário G — Histórico importado

PatientHistory ≠ fila de resultados modernos. Sem validar/publicar o texto antigo.

---

## 35. Não fazer (cumprido)

Sem LIS, equipamentos, códigos de barras, stock lab, IA, catálogo novo, alteração Receção/Médico/billing, novos exames.

---

## 36. Prioridades

### P0 — clínico / privacidade / integridade

*Nenhum bloqueio P0 aberto no caminho consulta + regularização + validar,* com os gates Sprint 25 no código. Resultados não validados **não** vão ao médico.

(Vigilância: se no futuro `mark_lab_order_billed` for usável por perfil sem Receção — ver auditoria ENFERMEIRO — isso é P0 **desse** perfil, não do técnico lab.)

### P1 — piloto

1. **Walk-in** (exame sem consulta) — se a clínica o fizer no dia a dia, o piloto lab fica incompleto. Se todos os exames nascem da consulta, **não** bloqueia.  
2. Campo **ID cru** no create de resultado sem contexto de utente.  
3. Sem **cancelar** pedido lab errado (operações de correcção manuais).

### P2 — útil

1. Estado/copy da colheita invertidos; colheita sem tipo de amostra.  
2. «Publicar/entregue» vs validar (fricção + KPIs).  
3. Parâmetros não ligados ao catálogo (trabalho extra no hemograma).  
4. Role dashboard sem «aguardam validação» / regularização.  
5. Pesquisa ausente em colheitas e processamento.  
6. Sem revisão após validação.  
7. Conclusão do lab escrita em `clinical_notes` da consulta (mistura de artefactos).

### P3

Logo placeholder na impressão; audit de print; setas no copy; toast «Pedido concluído».

---

## 37. Recomendação

**UAT presencial do caminho:** consulta → Receção regulariza → lab recebe/processa/regista/valida → médico vê na consulta.

**Não** abrir sprint de LIS nem catálogo de parâmetros até a clínica confirmar walk-in e o significado de «entregue».

Workaround walk-in (se aparecer na UAT): Receção abre atendimento/consulta administrativa e o médico (ou fluxo existente) pede o exame — **não é produto**; é processo. Não implementar pedido órfão nesta auditoria.

---

## Fontes

- `backend/apps/laboratory/constants.py`, `models.py`, `billing.py`, `validators.py`  
- `backend/apps/laboratory/services/laboratory_service.py`, `laboratory_result_service.py`  
- `backend/apps/laboratory/filters.py`, `ordering.py`, `permissions.py`  
- `backend/apps/appointments/services/clinical_record_service.py`  
- `backend/apps/reception/views.py` (`mark_lab_order_billed`)  
- `backend/apps/users/management/commands/seed_rbac.py`  
- `backend/apps/data_migration/apply.py`  
- `frontend/src/pages/dashboards/LaboratoryRoleDashboardPage.tsx`  
- `frontend/src/features/laboratory/**`  
- `frontend/src/components/print/LabResultPrint.tsx`  
- Testes: `test_laboratory.py`, `test_laboratory_results.py`, `test_laboratory_hardening_sprint25.py`
