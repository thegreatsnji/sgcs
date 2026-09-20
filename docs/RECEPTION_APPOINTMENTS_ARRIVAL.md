# Polimento operacional — Marcações (Receção)

**Data:** 2026-08-20  
**Estado:** `APPOINTMENTS_ARRIVAL_READY`  
**Âmbito:** eliminar a separação operacional entre paciente marcado e walk-in, sem nova arquitectura.

---

## Handoff reutilizado (decisão)

| Peça | Serviço / fluxo |
|---|---|
| Chegada física | `ReceptionService.check_in` — mesmo check-in + `WaitingQueue` de Atendimento rápido / Fila da Receção |
| Encaminhamento posterior | `ReceptionService.assign_to_doctor` → `AppointmentService.create_from_handoff` |
| Anti-duplicação no handoff | `create_from_handoff` **reutiliza** a marcação já ligada ao mesmo `check_in` (não cria segunda consulta) |

Não foi criada fila nova, modelo novo, nem módulo novo.

---

## Alteração de API (necessária)

### `POST /api/v1/appointments/{id}/confirm-arrival/`

| | |
|---|---|
| Permissão | `appointments.confirm` (já no seed RECECIONISTA; **sem** alteração de RBAC/JWT) |
| Efeito | Liga a marcação a um `ReceptionCheckIn` + entrada na fila da Receção; estado → `EM_ESPERA` |
| Idempotência | Repetir o POST devolve a mesma marcação / mesmo `check_in` — não cria segunda consulta nem segunda fila |
| Restrição | Só marcações do **dia**; estados finais / em consulta são rejeitados |

**Porquê novo endpoint:** `POST .../confirm/` continua a significar apenas `AGENDADA` → `CONFIRMADA` (confirmação de agenda, não chegada). Misturar os dois no mesmo endpoint quebraria o significado operacional.

Endpoints existentes mantidos: `confirm`, `cancel`, `start` (RBAC inalterado).

---

## UI (RECECIONISTA)

| Antes | Depois |
|---|---|
| «Confirmar» | «Confirmar marcação» |
| — | «Confirmar chegada» (marcações do dia sem check-in) |
| «Iniciar» visível sem permissão | Escondido sem `appointments.start` |
| Cancelar só na API | «Cancelar marcação» (estado `CANCELADA`, sem apagar) |

Menu: Marcações permanece **abaixo de Pacientes**.

---

## Testes

`apps/appointments/tests/test_confirm_arrival.py` — chegada, idempotência, handoff sem duplicar, cancelamento, visibilidade por perfil (Receção vs Médico).
