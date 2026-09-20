# Auditoria — Marcações (Receção / RECECIONISTA)

**Data:** 2026-08-20  
**Âmbito:** menu e fluxo de Marcações para o perfil RECECIONISTA.  
**Estado:** `APPOINTMENTS_AUDIT_COMPLETE` → implementação de chegada em `docs/RECEPTION_APPOINTMENTS_ARRIVAL.md` (`APPOINTMENTS_ARRIVAL_READY`).
**Código nesta tarefa:** nenhuma alteração (só documentação).

---

## 1. Inventário do que existe

### Frontend (rotas sob `appointments.view`)

| Rota | Página | Função aparente |
|---|---|---|
| `/appointments` | Agenda médica (dashboard) | Resumo / agenda do dia |
| `/appointments/calendar` | Calendário | Vista por intervalo de datas |
| `/appointments/list` | Lista | Lista filtrável por estado |
| `/appointments/queue` | «Fila médica» | Fila de consultas (CONFIRMADA / EM_ESPERA / EM_CONSULTA) |
| `/appointments/new` | Nova consulta | Criar marcação |
| `/appointments/:id` | Detalhe | Ver / acções |
| `/appointments/:id/edit` | «Reagendar» | Alterar `scheduled_at` |

Sub-nav: Agenda diária · Calendário · Lista · Fila médica · + Nova consulta.

**Menu Receção:** `Marcações` → `/appointments` (`navigation.ts` + `UI_COPY.nav.appointmentsSchedule`).

### Backend (principais)

| Endpoint | Permissão típica | Notas |
|---|---|---|
| `GET/POST /api/v1/appointments/` | view / create | CRUD lista |
| `PATCH /api/v1/appointments/{id}/` | edit | Inclui reagendar via `scheduled_at` |
| `POST .../confirm/` | confirm | `AGENDADA` → `CONFIRMADA` |
| `POST .../cancel/` | cancel | Existe; UI Receção **não** chama |
| `POST .../start/` · `.../finish/` | start / finish | Só médico (serviço + RBAC) |
| `GET .../today/` · `.../calendar/` · `.../queue/` | view | Consultas |
| `POST .../follow-up/` | followup | Grava seguimento clínico; **não** cria nova marcação |
| `POST /api/v1/followups/` (módulo doctors) | doctors.followup | **Cria** nova consulta; Receção **sem** esta permissão |

### RBAC RECECIONISTA (seed)

**Tem:** `appointments.view`, `create`, `edit`, `confirm`, `cancel`.  
**Não tem:** `start`, `finish`, `delete`, `clinical`, `followup`, `doctors.followup`.

### Estados (`AppointmentStatus`)

| Código | Label UI actual |
|---|---|
| AGENDADA | Agendada |
| CONFIRMADA | Confirmada |
| EM_ESPERA | Em espera |
| EM_CONSULTA | Em consulta |
| CONCLUIDA | Concluída |
| CANCELADA | Cancelada |
| FALTA | Falta |

Lista UI filtra: Todos, Agendada, Confirmada, Em espera, Em consulta, Concluída — **sem** Cancelada/Falta nos filtros.

`FALTA`: existe no enum/labels; **não** há fluxo de UI que o atribua.

---

## 2. O que a rececionista consegue fazer hoje em Marcações

| Acção | Existe na UI? | Funciona para RECECIONISTA? | Notas |
|---|---|---|---|
| Criar marcação (paciente + data/hora + prioridade + motivo) | SIM | SIM | **Sem** selector de médico no formulário (campo API opcional não exposto) |
| Ver marcações (lista / calendário / hoje) | SIM | SIM | |
| Pesquisar / filtrar por estado | PARCIAL | SIM | Sem filtros Hoje/Amanhã/Semana dedicados na lista; sem filtro por telefone/médico na UI de lista |
| Ver médico / hora / paciente / estado | SIM | SIM | |
| Confirmar marcação | SIM | SIM | Botão «Confirmar» = `AGENDADA`→`CONFIRMADA` (**não** é «chegou à clínica») |
| Reagendar (mudar data/hora) | SIM | SIM | Página Editar só altera `scheduled_at` |
| Mudar médico no reagendamento | NÃO | — | UI de edit não muda médico |
| Cancelar | NÃO (UI) | API+RBAC SIM | `appointmentsService.cancel` existe; **nenhuma página o chama** |
| Confirmar chegada / check-in a partir da marcação | NÃO | — | Lacuna principal |
| Transformar marcação → fila / Atendimento rápido | NÃO | — | Fluxos desligados |
| Iniciar consulta | Botão VISÍVEL | NÃO | Sem `appointments.start`; backend exige médico → acção morta / erro |
| Marcar falta | NÃO | — | |
| Associar serviço de catálogo à marcação | NÃO | — | Serviço/faturação é outro fluxo |

---

## 3. Walk-in vs marcação

**Não há flag `walk_in` / origem no modelo.** A distinção é pelo caminho de criação:

| | Marcação prévia | Walk-in / dia |
|---|---|---|
| Entrada | `POST /appointments/` (UI Marcações) | Receção: check-in → fila → `assign_to_doctor` → `create_from_handoff` |
| Estado inicial | `AGENDADA` | `EM_ESPERA` |
| Ligações | tipicamente sem `check_in` / `queue_entry` | com check-in, referral, queue |

### Fluxos desejados vs realidade

**WALK-IN (já operacional no SGCS)**  
Paciente chega → **Atendimento rápido** → triagem → faturação → fila → médico.

**MARCAÇÃO (incompleto no SGCS)**  
Paciente agendado → localizar em Marcações → «Confirmar» (só estado de agenda) → **falta** «chegou» → **falta** entrada na fila/atendimento sem duplicar.

Depois da chegada, o ideal seria reutilizar Atendimento rápido / fila; **hoje isso não está ligado** à marcação prévia.

---

## 4. Duplicações / fricção

| Superfície | Função | Sobreposição com Marcações |
|---|---|---|
| Atendimento rápido | Dia: registo → pagar → médico | Cria consulta por handoff; **não** usa Marcações |
| Fila de atendimento | Fila da Receção (`WAITING`/`CALLED`…) | **Diferente** da «Fila médica» em `/appointments/queue` |
| Pacientes | Ficha / pesquisa | Partilha paciente; sem wizard de marcação embutido |
| Marcações | Agenda futura + confirmar booking | Não conduz o dia operacional |

**Fricção típica se a pessoa já estava marcada:**  
Abrir Marcações → (não há chegada) → abrir Atendimento rápido / Pacientes outra vez → risco de **segunda** consulta/check-in sem ligação à marcação original.

Duas «filas» com nomes próximos aumentam confusão (Receção vs médica).

---

## 5. Consultas operacionais («quem está marcado?»)

| Pergunta | Possível hoje? |
|---|---|
| Marcados hoje | SIM (dashboard / today / agenda) |
| Marcados amanhã | PARCIAL (calendário ou lista sem atalho «Amanhã») |
| Próximas marcações | PARCIAL |
| Com qual médico | SIM (se preenchido); criação Receção muitas vezes **sem médico** |
| Para qual serviço | NÃO na entidade consulta |
| A que horas | SIM |
| Qual estado | SIM |

---

## 6. Estados — copy operacional

Labels actuais já em Português e razoáveis.  
**Atenção semântica:** «Confirmada» ≠ «Chegou».  
Não inventar estados novos sem backend.  
Se no futuro existir chegada: preferir acção «Confirmar chegada» que ligue a check-in/fila, **sem** reutilizar o botão «Confirmar» actual sem clarificar copy.

---

## 7. Acção mais importante — «Confirmar chegada»

| | |
|---|---|
| Existe? | **SIM** (após polimento — ver `docs/RECEPTION_APPOINTMENTS_ARRIVAL.md`) |
| Endpoint | `POST /api/v1/appointments/{id}/confirm-arrival/` |
| Handoff | `ReceptionService.check_in` + ligação à marcação; `create_from_handoff` reutiliza a mesma consulta |

---

## 8. Reagendamento

| | |
|---|---|
| Mudar data/hora | **SIM** (edit + PATCH) |
| Mudar médico | **NÃO** na UI de edit |
| Complexidade | Simples (adequado) |

---

## 9. Cancelamento

| | |
|---|---|
| UI | **NÃO** |
| API + permissão Receção | **SIM** |
| Soft delete / histórico | Cancelamento por estado `CANCELADA` (não apagar) — padrão do serviço |

---

## 10. Controlo / seguimento

| Mecanismo | Cria marcação? | Receção |
|---|---|---|
| Separador clínico `POST .../follow-up/` | **NÃO** (só registo Seguimento) | Sem permissão |
| Módulo doctors `POST /followups/` | **SIM** (nova consulta) | Sem permissão; feito pelo médico |

**Conclusão:** parcial — o médico pode gerar retorno que cria consulta; a Receção não gere isso em Marcações de forma explícita, mas a consulta pode aparecer na lista.

---

## 11. Classificação para RECECIONISTA

| Classificação | Aplicação |
|---|---|
| **SECUNDARIO** | Trabalho diário se a clínica for sobretudo **walk-in** (fluxo SauVida actual centrado em Atendimento rápido) |
| **IMPORTANTE** | Se a clínica **usa marcação prévia** com frequência (telefone / retorno) |

Para o piloto SauVida, com Atendimento rápido + Fila como eixo: **SECUNDARIO**, mantendo a funcionalidade disponível.

---

## 12. Recomendação de menu (NÃO executar automaticamente)

**Opção recomendada: B** — manter «Marcações» no menu, **abaixo de Pacientes**, como função secundária.

Justificação:

- O módulo é real e útil para agendar e ver o dia.
- Não é o caminho do atendimento do dia (walk-in).
- Remover do menu (C) ou do piloto (D) só após confirmação presencial de que quase não há pré-marcação.
- Não escolher A (prioridade igual a Atendimento/Fila) enquanto «Confirmar chegada» não existir.

**Alternativa C** se a entrevista clínica confirmar: «quase ninguém marca com antecedência; só walk-in» — então retirar do menu principal e aceder via atalho interno / lista a partir de Pacientes, sem apagar rotas.

---

## 13. Alterações futuras úteis (só se o produto decidir)

1. Acção **Confirmar chegada** → check-in/fila/atendimento **reutilizando** fluxo actual (sem duplicar paciente/consulta).  
2. UI de **Cancelar** (API já existe).  
3. Esconder ou desactivar **Iniciar** para Receção.  
4. Selector de **médico** na criação.  
5. Filtros **Hoje / Amanhã / Esta semana**.  
6. Clarificar copy: «Confirmar marcação» vs futura «Confirmar chegada».  
7. Unificar linguagem das duas filas.

**Nada disto foi implementado nesta tarefa.**

---

## 14. Gates

Sem alteração de código → sem build/lint obrigatório.
