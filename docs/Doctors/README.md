# Módulo Médico — SGCS

Prescrições, tratamentos, evolução clínica, alta médica e seguimento.

## Modelos

- `Prescricao` / `MedicamentoPrescrito` / `PlanoTerapeutico`
- `Tratamento`
- `EvolucaoClinica`
- `AltaMedica`
- `SeguimentoClinico`

## Endpoints

| Método | URL | Descrição |
|--------|-----|-----------|
| CRUD | `/api/v1/prescriptions/` | Prescrições |
| POST | `/api/v1/prescriptions/{id}/approve/` | Aprovar |
| POST | `/api/v1/prescriptions/{id}/finish/` | Concluir |
| GET | `/api/v1/prescriptions/history/?paciente_id=` | Histórico |
| CRUD | `/api/v1/treatments/` | Tratamentos |
| POST | `/api/v1/treatments/{id}/finish/` | Concluir tratamento |
| CRUD | `/api/v1/evolutions/` | Evolução clínica |
| CRUD | `/api/v1/discharges/` | Alta médica |
| CRUD | `/api/v1/followups/` | Seguimento (cria consulta futura) |

## Permissões RBAC

`doctors.prescription` · `doctors.treatment` · `doctors.evolution` · `doctors.discharge` · `doctors.followup`

## Integrações

- **Consultas** — cada registo ligado a `Appointment`
- **Pacientes** — histórico terapêutico por paciente
- **Appointments** — seguimento cria consulta automaticamente via `AppointmentService`
- **Auditoria** — `PRESCRICAO_CRIADA`, `TRATAMENTO_CRIADO`, `EVOLUCAO_ADICIONADA`, `ALTA_MEDICA`, `SEGUIMENTO_AGENDADO`
- **Event Bus** — `doctor.prescription.created`, `doctor.discharge.created`, `doctor.followup.created`
- **Redis** — cache histórico (TTL 120s)

## Frontend

Rotas: `/doctor`, `/doctor/prescriptions`, `/doctor/treatments`, `/doctor/history`, `/doctor/discharge`

Componentes em `frontend/src/features/doctors/`.
