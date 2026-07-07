# Feature: Pacientes

Módulo de gestão de utentes — **implementado na Sprint 4**.

## Estrutura

| Área | Localização |
|------|-------------|
| Páginas | `src/features/patients/pages/` |
| Componentes | `src/features/patients/components/` |
| Serviço API | `src/services/patients/` |
| Tipos | `src/types/patient.ts` |
| Schemas Zod | `src/schemas/patientSchema.ts` |
| Backend | `backend/apps/patients/` |

## Rotas

- `/patients` — Lista (requer `patients.view`)
- `/patients/new` — Novo (requer `patients.create`)
- `/patients/:id` — Detalhes
- `/patients/:id/edit` — Editar
- `/patients/:id/clinical` — Ficha clínica
- `/patients/:id/documents` — Documentos
- `/patients/:id/history` — Histórico

## Documentação

Ver `docs/Patients/` na raiz do projeto.
