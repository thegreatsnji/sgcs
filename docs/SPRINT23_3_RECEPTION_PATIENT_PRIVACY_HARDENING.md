# Sprint 23.3 — Hardening privacidade Pacientes (Receção)

**Data:** 2026-08-20  
**Base:** `docs/RECEPTION_PATIENTS_AUDIT.md`  
**Estado:** `RECEPTION_PATIENTS_READY`

---

## Objectivo

Separar **dados administrativos** de **dados clínicos** para `RECECIONISTA` (backend + frontend), e acrescentar a ponte **Ficha → Novo atendimento → Atendimento rápido** sem redesenhar Pacientes.

---

## Endpoints auditados e exposição

| Endpoint | View / serializer | Antes (Receção) | Depois |
|---|---|---|---|
| `PATCH …/patients/{id}/allergies/` | `PatientAllergyViewSet` | Escrita via `patients.edit` | **403** — `HasPatientClinicalWritePermission` (`appointments.clinical`) |
| `PATCH …/chronic-diseases/` | `PatientChronicDiseaseViewSet` | Escrita via `patients.edit` | **403** escrita; **lista vazia** para não-clínicos |
| `PATCH …/observations/` | `PatientObservationViewSet` | Escrita via `patients.edit` | **403** escrita; lista só `ADMINISTRATIVA` |
| `GET …/appointments/{id}/` | `AppointmentSerializer` | `diagnosis`, `clinical_notes`, `notes` | Campos clínicos **omitidos** sem `appointments.clinical` |
| `GET …/patients/{id}/appointments/` | Idem + context request | Idem | Idem (context corrigido) |
| `GET/PATCH …/appointments/{id}/clinical/` | `clinical_record` | GET com `appointments.view` | Exige **`appointments.clinical`** |
| `GET …/patients/{id}/history/` | `PatientHistorySerializer` | Descrição clínica completa | Eventos clínicos **redigidos** |
| `GET …/documents/` | queryset nested | Incluía `EXAME_EXTERNO` | Exclui tipos clínicos |
| `GET /laboratory/results/` | lab results | Sem permissão seed | Continua **403** |
| `POST …/history/` | ReadOnly | N/A | **405** (inalterado; confirmado em teste) |
| `POST …/confirm-imported-data/` | PatientViewSet | OK admin | Mantido; **não** altera provenance |

Frontend consumers: ficha (`PatientProfileShell`), tab Alertas clínicos (`PatientClinicalPage`), formulário (`PatientFormPage`), lista (`PatientsTable` / `PatientRowActions`), Atendimento (`ReceptionWorkflowPage` via `?paciente=`).

---

## Acesso removido (Receção)

- Escrita de alergias, doenças crónicas, observações
- Leitura de diagnóstico / notas médicas / `notes` em consultas
- Prontuário `…/clinical/`
- Detalhe de eventos clínicos em `PatientHistory` (descrição + metadata)
- Documentos `EXAME_EXTERNO`
- Grupo sanguíneo na resposta de detalhe e no formulário de criação/edição
- Contagem de doenças crónicas no detalhe (forçada a 0)

---

## Campos administrativos mantidos

Nome, telefone, residência/morada, sexo, data de nascimento, documento, contactos de emergência, pesquisa, registo, confirmação de dados importados, navegação operacional de consultas (data/estado/médico sem conteúdo clínico).

---

## Campos clínicos protegidos

Diagnóstico, notas médicas, observações clínicas, alergias (**edição**), doenças crónicas, prescrições (sem UI + sem permissão indevida), resultados laboratoriais detalhados, grupo sanguíneo (edição Receção), documentos de exame externo.

Alergias **permanecem legíveis** no balcão (segurança operacional); edição só com `appointments.clinical`.

---

## PatientHistory

- ViewSet **read-only**
- Tipos clínicos: descrição → texto genérico de redacção; `metadata` limpa
- Confirmação de dados importados **não** altera histórico
- Provenance do paciente (`migration_id`, `import_batch`, `source`, …) preservada no `confirm-imported-data`

---

## Documentos

Lista da Receção exclui `EXAME_EXTERNO`. Documentos administrativos (ex.: BI) continuam listáveis.

---

## CTA Novo atendimento

- Botão na ficha: `buildAtendimentoUrl({ passo: 1, paciente })` → `/reception/atendimento?passo=1&paciente={id}`
- Também no menu de acções da lista (se `reception.create`)
- Reutiliza fluxo existente; **não** cria paciente/consulta/fatura automaticamente

---

## Pacientes importados

Banner e «Confirmar dados» preservados. Confirmação = verificação **administrativa**, não clínica.

---

## Duplicados

Copy do aviso: «Pode já existir um utente com estes dados.» + «Ver utente existente». Continuar registo permanece possível (sem merge automático).

---

## UX

| Item | Decisão |
|---|---|
| Tab «Histórico» | Renomeada para **«Alertas clínicos»** (conteúdo era clínico) |
| «Última visita» | **«Última actualização»** (`updated_at`) |
| Datas UI | ISO → `DD/MM/AAAA` via `formatDisplayDate` |
| Grupo sanguíneo | Fora do formulário Receção; modelo intacto |

---

## Testes

`apps/patients/tests/test_reception_patient_privacy.py`:

- Capacidades administrativas Receção
- Escritas clínicas 403
- Scoping de leitura (consultas, crónicas, observações, history, documentos, lab)
- Provenance após telefone + confirmação
- Médico continua a ver diagnóstico e a criar alergias

---

## Gates

| Gate | Resultado |
|---|---|
| `python manage.py check` | OK |
| `python manage.py makemigrations --check` | No changes detected |
| `pytest -q --reuse-db` | **451 passed**, 2 skipped, **2 failed** (preexistentes: médico indisponível no handoff — fora de escopo) |
| `npm run build` | OK |
| `npm run lint` | 0 errors, 10 warnings preexistentes |

Suíte de privacidade: `test_reception_patient_privacy.py` — **17 passed**.

---

## Regressões evitadas

- `AppointmentSerializer` passa sempre `request` no context (Médico/Direção mantêm diagnóstico)
- Sem novas permissões no seed; gate clínico = `appointments.clinical` existente
- Faturação / Stock / Marcações / merge / portal — não alterados
