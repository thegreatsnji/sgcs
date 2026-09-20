# Atribuição de médico pela Receção

**Data:** 2026-08-20  
**Estado:** `RECEPTION_DOCTOR_ASSIGNMENT_READY`

---

## Auditoria (antes das alterações)

| Peça | Comportamento encontrado |
|---|---|
| `assign_to_doctor` | Criava `Referral.assigned_doctor` + `Appointment` via `create_from_handoff` |
| Disponibilidade | Médico «disponível» = sem consulta `EM_CONSULTA` no dia |
| Auto-assign | Backend fazia fallback para `suggested_doctor_id` (menor fila / habitual) |
| Fila UI | Botão «Médico» chamava API **sem** `doctor_id` |
| WaitingQueue | Não armazena médico; médico vive em Referral/Appointment |
| Painel médico | `get_doctor_queue` filtra `doctor=self` **ou** `doctor` null |

**Conflito resolvido:** auto-assign e atribuição cega na fila violavam a decisão operacional («a Receção escolhe»).

---

## Fluxo actual

Walk-in / Atendimento rápido:

1. Paciente → triagem/check-in  
2. Faturação/pagamento  
3. **Escolher médico** (passo 4)  
4. Encaminhar → WaitingQueue `IN_SERVICE` + Appointment `EM_ESPERA` com esse médico  
5. Médico vê na fila clínica

Marcações:

- Confirmar chegada preserva `Appointment.doctor`  
- Opções expõem `scheduled_doctor`  
- UI pré-selecciona se disponível; Receção confirma (sem auto-balanceamento)

---

## Regras

- `doctor_id` **obrigatório** na API  
- Apenas `UserRole.MEDICO` activos  
- Indisponível → erro controlado; utente permanece WAITING; pagamento intacto  
- Reatribuição permitida enquanto consulta ≠ `EM_CONSULTA`  
- Após iniciar consulta → bloqueada  
- Sem round-robin / menor fila automático

---

## UI

- Atendimento rápido: «Encaminhar para médico» + select com Disponivel / N em espera / Indisponível  
- Fila: coluna Médico (`Por atribuir` ou nome); «Atribuir médico» / «Alterar médico»  
- Filtro: Todos / Por atribuir / médico concreto  

---

## RBAC

Receção: `reception.edit` para atribuir. Sem `appointments.start` / clinical / alergias.
