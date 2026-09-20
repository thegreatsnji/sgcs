# Auditoria operacional — perfil ENFERMEIRO (SGCS SauVida)

**Data:** 2026-08-24  
**Base operacional:** Receção `RECEPTION_READY_FOR_UAT` · Médico `DOCTOR_READY_FOR_UAT` · Laboratório `LABORATORY_READY_FOR_UAT`  
**Âmbito original:** auditoria de leitura.  
**Hardening:** Sprint 26 — `docs/SPRINT26_NURSING_WORKFLOW_HARDENING.md`  
**Estado:** `NURSING_READY_FOR_UAT`  
**UAT enfermagem:** `docs/UAT_ENFERMAGEM_FINAL.md`

Código em `C:\PROJECTS\SGCS` (backend Django + frontend React).

---

## Sprint 26 — estado pós-hardening

A auditoria (`NURSING_WORKFLOW_AUDIT_COMPLETE`) encontrou P0 (expirado = «Sem stock»; regularização lab via `reception.edit`) e P1 (enfermeiro como rececionista, triagem ambígua, Ajuste/Perda só na API, `appointments.edit` amplo).

**Corrigido nesta sprint (sem módulo novo):**

- ENFERMEIRO isolado da Receção no seed e nas rotas; `reception.create` apenas para triagem.
- Regularização lab exige `reception.edit` **e** `billing.edit` → enfermeiro 403.
- `appointments.edit` removido do perfil; PATCH clínico/consulta 403.
- Estados de stock com precedência EXPIRADO > SEM_STOCK > PROXIMO_DA_VALIDADE > STOCK_BAIXO > DISPONIVEL.
- Saída bloqueada se expirado; Ajuste e Perda na UI; stock inicial por confirmar; duplicado exacto.
- Painel: KPIs de stock reais (baixo / sem / validade / expirados).

**DECISÃO_CLINICA_PENDENTE**

- Quem é o responsável principal pela triagem — Receção ou Enfermagem? (ambos podem triar temporariamente.)
- Notas de enfermagem, procedimentos (curativos, injecções, soroterapia) e administração de medicamento: **não implementados**. Validar no UAT presencial.

Prescrição **não** reduz stock automaticamente.

---

---

## Pergunta central

> Um enfermeiro da Clínica SauVida consegue realizar o seu trabalho diário no SGCS de forma simples, segura e sem assumir responsabilidades da Receção ou do Médico?

**Resposta:** **Ainda não, de forma isolada e segura para piloto.**

O ENFERMEIRO **consegue** registar triagem com sinais vitais e prioridade, e **consegue** gerir Entrada/Saída do Stock de Urgência com auditoria e bloqueio de stock negativo. O médico **vê** os vitais da triagem no prontuário (`sinais_vitais_triagem`).

Porém o perfil **assume trabalho da Receção** (fila, encaminhar médico, UI de atendimento, regularização de exames lab). **Não existe** fila de enfermagem, notas/procedimentos de enfermagem operacionais, nem administração de medicamento distinta da Saída de stock. A UI de stock **não** expõe Ajuste/Perda e **etiqueta itens expirados como «Sem stock»**.

Não se inventam protocolos (Manchester, farmácia, prontuário de enfermagem). Procedimentos não confirmados pela clínica ficam **AUSENTES**, não como backlog de produto inventado.

---

## 1. Painel do enfermeiro

**Rota home:** `/dashboard/nurse` — `NurseRoleDashboardPage`  
**Menu ENFERMEIRO:** Painel · Triagem (`/nursing/triage`) · Fila (`/reception/queue`) · Stock de Urgência (`/stock`) · Pacientes · Consultas

| Questão | Achado |
|---|---|
| Pacientes em triagem? | **Não** como lista. O painel mostra KPI «Na fila (receção)» = utentes na fila da Receção, não «à espera de triagem». |
| Encaminhados para enfermagem? | **Não.** `ReferralDepartment` só tem RECEÇÃO, MÉDICO, LAB, FATURAÇÃO. |
| Sinais vitais pendentes? | **Não.** Não há fila de vitais por fazer. |
| Procedimentos? | **Não** no painel nem noutro ecrã de enfermagem. |
| Stock baixo? | **Parcial.** O módulo `/stock` tem KPI «Stock baixo». O painel do enfermeiro **só** conta `quantidade_stock <= 0` e chama-lhe «sem stock». |
| Sem stock? | **Sim** no painel (até 5 nomes) e no `/stock`. |
| Próximos da validade? | **No `/stock`** (KPI). **Não** no painel do enfermeiro. |
| Tarefas do dia? | **Não.** Sem lista de tarefas. |
| Dashboard específico? | **Sim** (`/dashboard/nurse`), mas é um resumo de **páginas gerais** (triagem partilhada, fila da Receção, stock, agenda). |

**Copy:** «Registo clínico antes do pagamento na receção» — o enfermeiro é empurrado para o fluxo da Receção.

---

## 2. Responsabilidades reais no sistema

Permissões seed (`seed_rbac.py`, `UserRole.ENFERMEIRO`):

`patients.view`, `patients.create` · `appointments.view`, `appointments.edit` · `reception.view/create/edit` · `pharmacy.view/edit/create` · `stock.view/create/edit/entry/exit/adjust/history` · `dashboard.view`

**Não tem:** `billing.*`, `laboratory.*`, `appointments.clinical/diagnosis/start/finish/create`, `doctors.prescription`, `users.*`, `settings.*`, `notifications.view`.

| Acção | Classificação | Evidência |
|---|---|---|
| Pesquisar/registar utente e fazer check-in/triagem | **ESSENCIAL** | `POST /reception/check-in`; UI `/nursing/triage` |
| Sinais vitais na triagem (TA, T, peso; SpO₂/FC/FR/altura opcionais) | **ESSENCIAL** | `ReceptionCheckIn` + `triageSchema` |
| Cor de triagem Verde/Amarelo/Vermelho | **ESSENCIAL** | Obrigatória no wizard; mapeia prioridade da fila |
| Ver fila de espera da Receção | **ÚTIL** (contexto) / **INDEVIDA** se gere a fila | `/reception/queue` no menu |
| Chamar utente / alterar estado da fila | **INDEVIDA** | `reception.edit` → `PATCH queue` |
| Encaminhar para médico (`assign_to_doctor`) | **INDEVIDA** | `reception.edit`; UI na fila |
| Abrir atendimento da Receção (pagamento) | **INDEVIDA** | `/reception/atendimento` só exige `reception.view` |
| Marcar exame lab como regularizado | **INDEVIDA** / risco | `mark_lab_order_billed` aceita `reception.edit` **ou** `billing.edit` |
| Ver/criar/editar Stock de Urgência | **ESSENCIAL** | `/stock` |
| Entrada / Saída | **ESSENCIAL** | API + UI |
| Ajuste / Perda-expiração | **ESSENCIAL** no backend; **AUSENTE** na UI | endpoints existem; `UrgentStockPage` não |
| Histórico de movimentos | **ESSENCIAL** | `/stock/historico` |
| Notas de enfermagem persistentes | **AUSENTE** | tipo `ENFERMAGEM` no modelo; escrita exige `appointments.clinical` |
| Procedimentos (injecção, penso, soro) | **AUSENTE** | sem modelo operacional de enfermagem |
| Administração de medicamento (acto clínico) | **AUSENTE** | só Saída de stock, opcionalmente com utente (API) |
| Diagnóstico / SOAP / prescrição | **INDEVIDA** (bloqueada) | 403 / «Apenas médicos» |
| Iniciar/concluir consulta | **INDEVIDA** (bloqueada) | sem `appointments.start/finish` |
| PATCH consulta (hora, médico, queixa, notas) | **INDEVIDA** (permitida) | tem `appointments.edit` |
| Faturar / receber pagamento | **INDEVIDA** (API 403) | sem `billing.*`; UI de Receção ainda mostra atalhos |
| Ver alergias (leitura) | **ESSENCIAL** (segurança) | `patients.view`; edição clínica bloqueada |
| Criar paciente | **ÚTIL** | necessário se o utente ainda não existe na triagem |
| Editar ficha do utente | **AUSENTE** | sem `patients.edit` (atalho na triagem leva a 403) |
| Agenda / consultas do dia | **SECUNDÁRIA** | vê KPIs globais; não inicia consulta |
| Laboratório (pedidos/resultados) | **AUSENTE** (correcto) | sem `laboratory.*` |
| Gestão de utilizadores / configuração | **AUSENTE** (correcto) | |

---

## 3. Triagem

**Quem pode iniciar:** `RECECIONISTA` e `ENFERMEIRO` (`ReceptionService._ensure_receptionist`). Admin/superuser também.

**Quem pode editar depois:** **Ninguém** via API de check-in. Não há PATCH de `ReceptionCheckIn`. Vitais e cor ficam congelados no momento do check-in.

**Quem pode concluir:** O próprio `POST check-in` cria o check-in `WAITING` e a entrada na fila. «Concluir triagem» = submeter o wizard. Não há estado «triagem em curso» separado.

**Campos (modelo `ReceptionCheckIn`):**

| Campo | UI | Obrigatório no wizard |
|---|---|---|
| Utente | pesquisa / registo rápido | Sim |
| Cor de triagem | Verde / Amarelo / Vermelho | Sim |
| Peso (kg) | Sim | Sim |
| Altura (cm) | Sim | Não |
| Raça | Sim | Não |
| Temperatura (°C) | Sim | Sim (30–43) |
| Pressão arterial | `120/80` | Sim |
| SpO₂ (%) | Sim | Não |
| FC (b/min) | Sim | Não |
| FR (c/min) | Sim | Não |
| Queixas (`symptoms`) | Sim | Sim (mín. 3 caracteres) |
| Notas (`notes`) | «Notas adicionais» | Não |
| Tipo visita | CONSULTA / CONTROLE | Sim — copy de **faturação** |
| Idade na triagem | Calculada da DN | Sim (indirecto) |
| Actor | FK `receptionist` = utilizador autenticado | Automático |
| Timestamps | `check_in_time`, `created_at` | Automático |

**Prioridade da fila:** derivada da cor (`GREEN→NORMAL`, `YELLOW→HIGH`, `RED→EMERGENCY`). Altera posição na fila (`PRIORITY_ORDER`).

**Actor:** o enfermeiro é gravado em `receptionist`. A UI mostra o nome se `role === ENFERMEIRO`; o campo de modelo chama-se «Rececionista». Auditoria: `AuditAction.RECEPTION_CHECK_IN`.

**O ENFERMEIRO consegue triagem completa?** **Sim** — o mesmo `TriageCheckInWizard` da Receção.

**A RECEÇÃO continua podendo fazer triagem?** **Sim** — `/reception/check-in` e passo de triagem em `/reception/atendimento`.

**Duplicação de responsabilidade?** **Sim, total.** Os dois perfis executam o **mesmo** acto (vitais + cor + queixas + tipo de faturação) e o segundo check-in do mesmo utente activo é recusado («já se encontra na fila»). Não há divisão «enfermeiro vitais / receção pagamento» no modelo — só na copy da página de enfermagem.

**Não alterado nesta auditoria.**

---

## 4. Sinais vitais

### 4.1 Vitais da triagem (`ReceptionCheckIn`)

| Campo | Unidade | Origem | Obrigatório | Quem edita | Histórico |
|---|---|---|---|---|---|
| `weight` | kg | Wizard triagem | Sim (UI) | Só no check-in; depois imutável | Check-in + audit RECEPTION_CHECK_IN |
| `height_cm` | cm | Wizard | Não | Idem | Idem |
| `temperature` | °C | Wizard | Sim | Idem | Idem |
| `blood_pressure` | mmHg texto `SYS/DIA` | Wizard | Sim | Idem | Idem |
| `spo2` | % | Wizard | Não | Idem | Idem |
| `heart_rate` | b/min | Wizard | Não | Idem | Idem |
| `respiratory_rate` | c/min | Wizard | Não | Idem | Idem |

Alertas de valor fora do habitual existem no wizard (`getVitalWarnings`) mas **não bloqueiam** gravar.

Não há histórico de revisões: um check-in = um conjunto de vitais. Check-ins anteriores do mesmo utente permanecem como registos distintos.

### 4.2 Vitais da consulta (`SinaisVitais` no prontuário)

Registados **só pelo médico** (`ClinicalRecordService.guardar_sinais_vitais` — teste «Apenas médicos»; API `appointments.clinical`). Independentes da triagem. **Não** substituem nem actualizam o check-in.

### 4.3 Integração com o médico

**Confirmado (Sprint 24):** o prontuário expõe `sinais_vitais_triagem` a partir de `appointment.check_in`, com `origem: "TRIAGEM"`. A UI médica mostra o card **«Sinais vitais da triagem»** (TA, FC, FR, T, SpO₂, peso/altura) **sem cópia silenciosa** para o formulário do médico (há acção explícita de copiar se o médico quiser).

O enfermeiro **não** pode alterar vitais da triagem depois da consulta iniciada — **não há API**. Também não pode gravar vitais da consulta.

---

## 5. Prioridade / triagem (cores)

| Cor | Rótulo PT | Prioridade fila | Espera estimada (código) |
|---|---|---|---|
| GREEN | Verde — «Estável» | NORMAL | 120 min |
| YELLOW | Amarelo — «Prioritário» | HIGH | 90 min |
| RED | Vermelho — «Emergência» | EMERGENCY | 0 min (imediato) |

Não é protocolo de Manchester. Sem códigos numéricos. Sem azul/branco/preto.

| Questão | Achado |
|---|---|
| Quem define? | Quem faz o check-in (Receção **ou** Enfermagem). |
| Obrigatória? | **Sim** no wizard. |
| Altera ordem da fila? | **Sim.** |
| Médico vê? | Prioridade da consulta/handoff; a cor está no check-in ligado. Fila médica ordena por `scheduled_at` (auditoria médica). |
| Receção vê? | **Sim** — `TriageBadge` na fila. |

---

## 6. Encaminhamento

**O que existe:**

```
Check-in (Receção ou Enfermeiro)
  → WaitingQueue (fila única da Receção)
  → (Receção) pagamento
  → assign_to_doctor
  → Referral RECEPTION → DOCTOR + Appointment
  → fila/prontuário do médico
```

Não existe destino `NURSING`. Não existe «Médico → enfermagem/procedimento» como fila.

| Questão | Achado |
|---|---|
| Fila de enfermagem? | **Não.** |
| Paciente atribuído ao enfermeiro? | **Não.** |
| Enfermagem trabalha pela fila da Receção? | **Sim.** Menu aponta para `/reception/queue`. |

O enfermeiro, com `reception.edit`, **pode** ele próprio encaminhar ao médico — responsabilidade da Receção.

---

## 7. Observações de enfermagem

| Aspecto | Achado |
|---|---|
| Campo dedicado? | **Modelo:** `PatientObservation.observation_type = ENFERMAGEM`. **Operacional:** o enfermeiro **não escreve** (escrita exige `appointments.clinical`) e **não lê** observações não administrativas (queryset filtra só `ADMINISTRATIVA` sem `appointments.clinical`). |
| Notas na triagem | `ReceptionCheckIn.notes` — texto livre, visível a quem vê o check-in (Receção incluída). **Não** é nota clínica de enfermagem. Receção **pode** preencher o mesmo campo se for ela a fazer triagem. |
| Médico vê notas de triagem? | Queixas da triagem aparecem no cabeçalho da consulta; `notes` do check-in não é o SOAP. |
| Substitui diagnóstico? | **Não** — diagnóstico exige `appointments.diagnosis`. |

**Lacuna:** não há notas de enfermagem utilizáveis pelo perfil ENFERMEIRO. Não criar prontuário nesta auditoria.

---

## 8. Procedimentos

| Tipo | Existe no SGCS operacional? |
|---|---|
| Injecção | **Não** (além de itens de stock, ex. «inj.» no nome) |
| Curativo/penso | **Não** (material no stock, sem acto) |
| Soroterapia | **Não** |
| Administração de medicamento | **Não** como acto; há Saída de stock |
| Categoria faturação `ENFERMAGEM` | **Sim** no catálogo de faturação — acto da **Receção/cobrança**, não execução de enfermagem |

Sem modelo de procedimento ligado à consulta. Sem histórico de «procedimento realizado». Texto livre só nas notas de check-in.

**E2E D:** fluxo «encaminha → enfermeiro regista procedimento → histórico» **não existe**. Documentado; não implementado.

---

## 9. Administração de medicamento

| Conceito | Comportamento actual |
|---|---|
| PRESCRIÇÃO | Médico, módulo `doctors` / `PrescriptionService`. Exige permissão de prescrição. Enfermeiro **403** em diagnóstico; sem `doctors.prescription`. |
| ADMINISTRAÇÃO | **Não existe** modelo «medicamento administrado». |
| STOCK | Saída manual. API aceita `paciente` e `consulta` opcionais. UI de Saída **não** pede utente nem consulta. |

Prescrição **não** decrementa stock (`PrescriptionService` não referencia `MedicamentoUrgencia`). **Esperado: NÃO. Confirmado: NÃO.** Sem risco de ligação automática.

O enfermeiro pode (e deve, se usar o item) registar **Saída** à parte. Isso **não** prova administração clínica.

---

## 10. Stock de Urgência — módulo actual

**Modelos:** `MedicamentoUrgencia`, `MovimentoStockUrgencia` (`apps/pharmacy/`).  
**UI:** `/stock` (`UrgentStockPage`), `/stock/historico`.  
**Permissões ENFERMEIRO:** alinhadas com o pedido (ver, criar, entrada, saída, ajuste, histórico).

| Capacidade pedida | Backend | UI enfermeiro |
|---|---|---|
| Visualizar stock | Sim | Sim |
| Pesquisar | Sim (`codigo`, `nome`, `forma_apresentacao`) | Sim |
| Criar item | Sim | Sim («+ Novo item») |
| Entrada | Sim | Sim |
| Saída | Sim | Sim (bloqueia > stock) |
| Ajuste | Sim (`quantidade` = **novo saldo**) | **Não** |
| Perda/Expiração | Sim (`/perda`) | **Não** |
| Histórico | Sim (imutável) | Sim |
| Stock mínimo | Sim | Sim (criar + coluna) |
| Validade | Campo + estados | KPI no topo; **não** no formulário novo; **não** coluna na tabela |
| Desactivar item | `PATCH activo` | **Não** |

Copy da página: «Não é farmácia comercial» — correcto.

---

## 11. Quantidade

| Regra | Estado |
|---|---|
| Quantidade actual nunca editada directamente | **Cumpre.** `quantidade_stock` read-only no serializer; `partial_update` remove o campo; admin Django readonly. |
| Entrada aumenta | **Cumpre.** Teste: 10+5=15. |
| Saída diminui | **Cumpre.** |
| Ajuste auditado | **Cumpre** na API (`AJUSTE`, audit `STOCK_AJUSTE`, antes/depois). UI ausente. |
| Perda diminui | **Cumpre** na API. UI ausente. |
| Stock negativo bloqueado | **Cumpre.** `PositiveIntegerField` + `StockUrgenciaError`. |
| Concorrência | **Cumpre.** `select_for_update()` no item. |
| Movimentos imutáveis | **Cumpre.** `save` com pk e `delete` levantam `ValueError`. |

Ajuste: o campo `quantidade` no movimento de ajuste é o **saldo pretendido**, não o delta. Delta gravado = `abs(depois-antes)` (mínimo 1 se igual — caso degenerado).

Motivo/observação: **opcional** na API. Ajuste sem motivo é possível.

---

## 12. Stock inicial

| Questão | Achado |
|---|---|
| «Stock inicial por confirmar»? | **Não** na UI. Existe classificação `PENDENTE_QUANTIDADE` só no **plano de importação** (`import_plan.py`), não como estado do item em produção. |
| «Definir stock inicial»? | No **criar item**, campo «Quantidade inicial» (default **0**). Se > 0, cria movimento `ENTRADA` com origem `STOCK_INICIAL` e motivo «Stock inicial». Se 0, o item fica a zeros até uma Entrada posterior. |
| Excel nesta auditoria | **Não importar.** Fotos = nomes de referência (`quantidade_texto_original` / `current_ops.py`). |

**Lacuna:** a enfermeira não vê na lista que a quantidade das fotos **não** é saldo físico. `quantidade_texto_original` não aparece na tabela.

---

## 13. Novo item (formulário UI)

| Pedido | No formulário actual |
|---|---|
| Nome | Sim * |
| Apresentação | Sim |
| Categoria | Sim (Medicamento / Material clínico / Teste rápido / Outro) |
| Unidade | Sim * (default «frasco») |
| Quantidade inicial | Sim * |
| Stock mínimo | Sim (default 5) |
| Validade | **Não** (API aceita) |
| Preço referência opcional | **Não na UI** (API aceita — campo desnecessário no ecrã de enfermagem; correcto omitir) |

Campos API extra não mostrados: `servico` (FK faturação), `quantidade_texto_original`, `observacoes`, `activo`. `servico` no write serializer é **desnecessário** para o enfermeiro e arrisca ligar stock a catálogo.

Sem verificação de nome duplicado na UI/API de create (só `codigo` único auto `STK-#####`). O import plan detecta `NOME_DUPLICADO`; o create interactivo **não**.

---

## 14–17. Movimentos (E2E B/C e lacunas)

### Entrada (testado em código)

Stock 10 + Entrada 5 → **15**. Movimento com tipo, actor (`operador`), `created_at`, `quantidade_antes/depois`, observação opcional. **OK.**

### Saída

Stock 15 − 3 → **12**. `> stock` → 400 «Stock insuficiente». Utente/consulta **opcionais na API, ausentes na UI**. Actor e audit **OK.** Sem idempotência: dois «Confirmar saída» consecutivos (dois pedidos) podem duplar — o botão desactiva só enquanto `isPending`.

### Ajuste

API: 20 → 18 via `AJUSTE` com `quantidade=18`. **Não edita o campo quantidade.** UI **inexistente** — lacuna de piloto para contagem física.

### Perda / expiração

Tipo `PERDA_EXPIRACAO`. Sem distinção danificado vs expirado vs perda. **Adequado** (não é farmácia). UI **inexistente**.

---

## 18. Alertas de stock

| Alerta | Onde | Comentário |
|---|---|---|
| Stock baixo | `/stock` KPI + filtro; API `estado=STOCK_BAIXO` | **Útil.** Painel enfermeiro **não** usa este critério. |
| Sem stock | Painel (qty=0) + `/stock` | **Útil.** |
| Próximo da validade | KPI `/stock`; API 30 dias (`STOCK_URGENCIA_DIAS_PROXIMA_VALIDADE`) | **Útil**, mas sem filtro dedicado na barra de pills e sem coluna validade. |
| Expirado | API `EXPIRADO`; KPI `expirados` no dashboard JSON | **P0 UX:** `operationalStatus()` trata `EXPIRADO` com o rótulo **«Sem stock»**. Item expirado com quantidade > 0 parece ruptura, não validade. |

Filtros UI: Todos / Medicamentos / Materiais / Testes / Stock baixo / Sem stock. **Falta** Expirado e Próximo da validade.

Volume de alertas: 4 KPIs no `/stock` é **aceitável**, não excesso. O painel do enfermeiro é **incompleto**, não excessivo.

---

## 19. Medicamentos das fotos

Lista em `apps/data_migration/current_ops.py` (`fonte_foto`, nomes, textos tipo `CX/50`, `2CX/10`). Comentários no código: **não converter** texto em unidades.

A UI **não** tem fluxo «confirmar item da foto». A enfermeira pode:

- criar item novo (incluindo nomes que não estão na foto);
- definir quantidade inicial no create ou via Entrada;
- **não** vê o texto original da foto na lista.

Quantidades nas fotos **não** devem ser assumidas como stock actual — o sistema também **não** as assume no modelo (`quantidade_texto_original` separado de `quantidade_stock`).

---

## 20. Relação stock ↔ paciente

API: `paciente` e `consulta` opcionais em qualquer movimento. UI Entrada/Saída: **só quantidade + observação**. Fluxo **não fica lento** (2–3 cliques). Rastreabilidade por utente **não usada** no ecrã diário.

---

## 21. Relação prescrição ↔ stock

**Sem ligação automática.** Risco de decremento por prescrição: **nenhum.**

Risco inverso: stock pode ser saído **sem** prescrição — correcto para urgência, exige disciplina.

---

## 22. Privacidade

O enfermeiro **não** tem `appointments.clinical`. Aplica-se a mesma redacção que a Receção para conteúdo clínico detalhado.

| Recurso | Classificação | Notas |
|---|---|---|
| Alergias (leitura) | **NECESSÁRIO** | Segurança (ex. antes de usar stock). Edição bloqueada. |
| Doenças crónicas | Ocultas (lista vazia) | **ACEITÁVEL** |
| Diagnóstico / SOAP / notas médicas | API prontuário 403; appointments redige `diagnosis`, `clinical_notes`, `notes` | **NECESSÁRIO** estar bloqueado. Menu «Consultas» ainda abre ecrãs clínicos → erro. |
| Prescrição | Sem permissão de escrita; nested `patients/.../prescriptions/` devolve stub `module_ready: false` | **ACEITÁVEL** |
| Resultados lab | Sem `laboratory.results.view`; tab Paciente escondida | **NECESSÁRIO** ausente (não precisa do resultado completo) |
| Faturação / pagamentos / saldo | Sem `billing.view`; tab Pagamentos escondida | Stubs `payments`/`balance` em pacientes com `patients.view` devolvem zeros e `module_ready: false` — **ACEITÁVEL** (não são dados reais) |
| Histórico importado | Leitura; eventos clínicos com descrição redigida; `PatientHistory` GET only | **ACEITÁVEL.** Evento `PAGAMENTO` no enum **não** está na lista redigida — se no futuro for preenchido, o enfermeiro veria detalhe financeiro. Hoje o tipo parece **não usado** em serviços. |
| Receita clínica (imprimir) | Fora do menu | **ACEITÁVEL** |
| Administração (users) | Sem `users.*` | **NECESSÁRIO** ausente |
| Tipo sanguíneo | Removido do serializer sem clinical | **ACEITÁVEL** (enfermagem poderia argumentar necessidade — não confirmar agora) |

---

## 23. RBAC — violações vs. esperado

**PODE (esperado vs real)**

| Esperado | Real |
|---|---|
| Triagem apropriada | **Sim**, mas idêntica à Receção e inclui tipo de faturação |
| Sinais vitais | **Sim** (só triagem) |
| Notas/procedimentos de enfermagem | **Não** (ausentes) |
| Stock + histórico | **Sim** (ajuste/perda só API) |

**NÃO PODE (esperado vs real)**

| Esperado | Real |
|---|---|
| Faturar / receber pagamento | API **403**. UI Receção **mostra** «Criar fatura e cobrar» se abrir `/reception/atendimento`. |
| Alterar catálogo/preço oficial | Sem `billing.edit` no catálogo. **Pode** `PATCH` `preco_referencia_fcfa` e `servico` no item de urgência (`stock.edit`). |
| Diagnosticar / prescrever | **403** / serviço médico. |
| Validar laboratório | Sem permissões lab. |
| Gerir utilizadores / configuração | **403**. |
| Encaminhar médico / gerir fila / regularizar lab | **Pode** — violação de fronteira Receção. |
| Editar consulta (hora, médico, queixa, `notes`) | **Pode** via `appointments.edit`. |

---

## 24. Paciente importado

Mesmas regras de privacidade. Histórico **read-only** (405 no POST). Proveniência em `metadata` (`source`, `migration_id`, etc.) — o enfermeiro **não** confirma importação (`confirm_imported_data` exige `patients.edit`). Não altera `PatientHistory`. Tab Pagamentos oculta. Conteúdo clínico antigo redigido.

---

## 25. Laboratório

**Acesso módulo lab:** nenhum (`laboratory.*` ausente; rotas com `PermissionRoute`).

**Excepção:** com `reception.view` abre `/reception/lab-orders` (lista de exames a regularizar na Receção) e, com `reception.edit`, **pode marcar regularizado**.

**Necessário para enfermagem diária?** **Não** (resultados completos). A lista de regularização **também não** é trabalho de enfermagem.

Classificação: acesso ao módulo lab = **correctamente ausente**. Acesso a `lab-orders` da Receção = **excesso**.

---

## 26. Faturação

Sem `billing.view/create/payment`. Rotas `/billing/*` bloqueadas no frontend.

| Risco | Gravidade |
|---|---|
| `mark_lab_order_billed` com `reception.edit` (OR) — abre o gate do lab sem pagamento real | **P0** |
| UI `/reception/atendimento` com botões de fatura (falham no destino) | **P1** UX / mistura de papéis |
| Stubs payments/balance | **P3** |
| `preco_referencia` no item de stock via API | **P2** |

---

## 27. Copy / UX (páginas do enfermeiro)

| Problema | Onde | Gravidade |
|---|---|---|
| Enums crus `ENTRADA`, `SAIDA`, `AJUSTE`, `PERDA_EXPIRACAO` | Histórico stock | P2 |
| Data `created_at` cortada estilo ISO (`slice(0,16)` + `T`→espaço) | Histórico | P2 |
| «Gerir stock →», «Ver todo o histórico →», «Abrir ficha →» | Painel / stock / triagem | P3 |
| EXPIRADO → rótulo «Sem stock» | Lista stock | **P0** |
| «Tipo de atendimento (faturação)» | Wizard usado pelo enfermeiro | P1 |
| «Medicamentos (urg.)» | Painel | P3 |
| FK/campo «Rececionista» para actor enfermeiro | Modelo / API | P2 |
| IDs crus | Pouco na UI de stock (mostra `codigo`) | Aceitável |
| Termos farmacêuticos | Página explica que não é farmácia | Aceitável |
| Português do wizard de triagem | Globalmente simples | Aceitável |

---

## 28. Fluxo E2E A — Triagem

**Desenho pretendido:** Receção check-in → Enfermeiro vitais/prioridade → Médico vê vitais.

**O que o sistema faz hoje:** Receção **ou** Enfermeiro executam o **check-in completo** (identidade + vitais + cor + tipo CONSULTA/CONTROLE). Não há passo «Receção só identifica» separado do wizard (salvo o pagamento **depois**, na Receção).

| Critério | Resultado |
|---|---|
| Mesmo utente / um check-in | **Sim**, se só um perfil submeter. Segundo check-in activo bloqueado. |
| Não duplica triagem | **Sim** ao nível de fila; **não** ao nível de papéis (dois sítios iguais). |
| Timestamps / actor | **Sim** (`check_in_time`, user no FK + audit). |
| Médico vê vitais | **Sim**, se a consulta nascer desse check-in (`assign_to_doctor`). |

Se a Receção fizer a triagem primeiro, o enfermeiro **não** volta a editar vitais.

---

## 29. Fluxo E2E B — Stock (Ceftriaxona)

API e testes cobrem: listar, Entrada, Saída, bloqueio negativo, actor, movimento. Pesquisa por nome funciona.

UI: procurar → Entrada/Saída → confirmar. Quantidade correcta se um movimento de cada vez.

**Lacuna:** se o item das fotos existir com stock 0, a enfermeira usa Entrada 5 depois Saída 1. Não há wizard «Ceftriaxona da foto».

---

## 30. Fluxo E2E C — Novo item

Categoria, unidade, quantidade inicial via movimento, stock mínimo: **sim** no create. **Sem** validade no form. **Sem** detecção de duplicado por nome. Código gerado automaticamente.

---

## 31. Fluxo E2E D — Procedimento

**Não existe.** Ver §8. Não implementar nesta auditoria.

---

## 32. Riscos de erro

| Risco | Mitigação actual | Falha residual |
|---|---|---|
| Paciente errado na triagem | Pesquisa + cabeçalho com número/nome; «Alterar paciente» | Sem confirmação biométrica; um clique em utente homónimo |
| Quantidade errada no stock | Preview «Novo stock»; max na Saída | Sem confirmação segunda pessoa; Ajuste invisível leva a usar Entrada/Saída de forma incorrecta |
| Saída duplicada | Botão pending; `select_for_update` | Dois pedidos HTTP após sucesso |
| Ajuste sem motivo | — | API permite; UI nem existe |
| Triagem editada depois | Imutável | Não dá para **corrigir** vitais errados (risco inverso) |
| Stock inicial duplicado | Create + Entrada posteriores | Dois creates do mesmo nome; ou inicial 0 + Entrada «Stock inicial» outra vez |
| Item duplicado | Só `codigo` único | Nomes iguais possíveis |
| Enfermeiro com acesso financeiro | Sem `billing.*` | **Regularização lab** via `reception.edit` |
| Enfermeiro com edição médica | Sem clinical/diagnosis/prescription | `appointments.edit` em queixa/notas/médico/hora; vitais de consulta bloqueados |

---

## 33. Cliques / fricção

**Triagem:** Painel → Nova triagem → pesquisar utente → (opcional registo) → cor + peso + TA + T + queixas + tipo visita → Guardar.

Classificação: **ACEITAVEL**. Um formulário longo, mas um submit. Fricção extra: copy de faturação e ficha «abrir para editar» sem `patients.edit`.

**Stock (Entrada/Saída):** Pesquisar → botão → quantidade → Confirmar.

Classificação: **ACEITAVEL** / próximo de **SEM_FRICCAO**.

**Stock (contagem física / validade / perda):** **BLOQUEANTE** na UI (Ajuste/Perda/validade no item).

---

## 34. Não fazer (esta auditoria — cumprido)

Não se criou módulo de Enfermagem, farmácia, fornecedores, compras, prontuário novo, IA, prescrição automática, nem se alterou Receção/Médico/Lab/catálogo, nem se importou stock, nem se adicionaram protocolos clínicos não confirmados.

---

## 35. Prioridades

### P0 — segurança clínica, privacidade, integridade

1. UI de stock classifica `EXPIRADO` como «Sem stock».  
2. ENFERMEIRO pode `mark_lab_order_billed` (`reception.edit` **OR** `billing.edit`) e furar o gate de regularização do Laboratório (Sprint 25).

### P1 — bloqueia piloto isolado / operação diária de stock e papéis

1. Perfil assume a Receção: fila (chamar/estado), `assign_to_doctor`, `/reception/atendimento`, `/reception/lab-orders`, subnav da Receção.  
2. Triagem 100% duplicada com a Receção, incluindo tipo de atendimento para faturação.  
3. Ajuste e Perda existem na API e nas permissões, **não** no ecrã.  
4. Sem validade no criar/editar item; texto das fotos e «quantidade por confirmar» invisíveis.  
5. `appointments.edit` no seed — PATCH de consulta (médico, hora, queixa, notas).  
6. Dashboard de enfermagem não mostra stock baixo/validade; só qty=0.  
7. Nomes de item duplicáveis.

### P2 — melhoria útil

1. Notas/procedimentos/administração de enfermagem **ausentes** — só avançar se a clínica confirmar o acto.  
2. Saída sem utente/consulta na UI.  
3. Histórico: enums e datas.  
4. PATCH `preco_referencia` / `servico` no item.  
5. Menu Consultas / ficha editar como beco sem saída.  
6. Sem desactivar item na UI; filtros Expirado/Validade.  
7. Ajuste sem motivo obrigatório.  
8. Impossibilidade de corrigir vitais de triagem (pode ser feature; documentar para UAT).

### P3 — opcional

Setas no copy, abreviações do painel, ícone de lab no KPI de medicamentos, rótulo «Rececionista» no actor.

---

## 36. Integração (resumo)

| Par | Comportamento |
|---|---|
| Receção | Mesmo check-in; fila partilhada; enfermeiro **pode** fazer o trabalho da Receção |
| Médico | Vitais da triagem visíveis; sem edição médica pelo enfermeiro no prontuário |
| Paciente | Pesquisa/criação na triagem; alergias visíveis; clínico detalhado redigido |
| Prescrição → stock | Sem ligação |

---

## 37. Recomendação

**Estado:** `NURSING_READY_FOR_UAT` após Sprint 26.

Workaround anterior (enfermeiro na fila/atendimento/regularização lab) **já não se aplica**. UAT: `docs/UAT_ENFERMAGEM_FINAL.md`.

Perguntas clínicas em aberto não bloqueiam o UAT técnico: responsável da triagem; notas/procedimentos/administração.

---

## Fontes (código)

- `backend/apps/users/management/commands/seed_rbac.py`  
- `backend/apps/reception/services/reception_service.py`  
- `backend/apps/reception/models.py`, `constants.py`, `permissions.py`  
- `backend/apps/pharmacy/models.py`, `services/stock_service.py`, `views.py`, `tests/test_pharmacy_urgent.py`  
- `backend/apps/appointments/permissions.py`, `services/clinical_record_service.py`  
- `backend/apps/patients/privacy.py`, `permissions.py`  
- `backend/apps/doctors/services/prescription_service.py`  
- `frontend/src/pages/dashboards/NurseRoleDashboardPage.tsx`  
- `frontend/src/features/nursing/pages/NurseTriagePage.tsx`  
- `frontend/src/features/reception/components/TriageCheckInWizard.tsx`  
- `frontend/src/features/pharmacy/pages/UrgentStockPage.tsx`  
- `frontend/src/constants/navigation.ts`, `frontend/src/routes/index.tsx`
