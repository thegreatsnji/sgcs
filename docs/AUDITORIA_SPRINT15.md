# Auditoria Sprint 15 — SGCS SauVida

**Data:** 2026-07-31  
**Papel:** Arquitectura de software e análise de sistemas clínicos  
**Âmbito:** Backend Django/DRF + Frontend React (Sprints 1–14); **sem alteração de código** nesta etapa  
**Contexto clínico confirmado:** faturação na Receção; sem internamento; sem farmácia comercial; medicamentos/materiais só para urgência e uso interno; perfis: Administrador, Direcção, Médico, Receção, Laboratório (código: `RECECIONISTA`)

---

## 1. Metodologia

Para cada área foram revistos, quando existem: modelos e migrations, serializers, services, views/viewsets, URLs (`/api/v1/…`), permissions/RBAC (`seed_rbac.py`, mixins), features frontend (`src/features/*`), rotas (`src/routes/index.tsx`), formulários/schemas, testes pytest, `AuditService`, e ligação a `billing.Servico` / faturação.

**Estados:** `CONCLUÍDO` · `PARCIAL` · `AUSENTE` · `NÃO APLICÁVEL`

---

## 2. Tabela de auditoria

| Funcionalidade | Estado | Backend | Frontend | Endpoints | Testes | Lacunas | Recomendação |
|---|---|---|---|---|---|---|---|
| **1. Receção** | PARCIAL | `apps/reception`: `ReceptionCheckIn`, `WaitingQueue`, `Referral`; triagem (`triage_color`, PA, sintomas — migration `0002_triage_fields`); `ReceptionService` + auditoria | `features/reception`: triagem (`TriageCheckInWizard`), fila, encaminhamentos, dashboard; rotas `/reception/*` | `POST /reception/check-in/`, `GET/PATCH /reception/queue/`, `POST assign-to-doctor`, `GET history`, `POST referrals` | `test_reception.py` (14 casos, incl. triagem) | **Receção sem `billing.*` no RBAC por defeito**; menu sem `/billing`; encaminhamento a `BILLING` existe mas sem fluxo financeiro integrado na receção | Alinhar RBAC e navegação da **Receção** com faturação na receção (sem novo perfil); UAT check-in→fila→cobrança |
| **2. Gestão de pacientes** | CONCLUÍDO | `apps/patients`: CRUD, soft delete, duplicados, histórico, anexos, alergias, doenças crónicas; `PatientService` + auditoria | `features/patients`: listagem, formulários, clínico, documentos, histórico; `/patients/*` | `GET/POST/PATCH/DELETE /patients/`, `check-duplicate`, `audit-trail`, recursos aninhados | `test_patients.py` (~23) | Seguro do paciente: API parcial, UI limitada | Manter; completar UI seguros se a clínica usar |
| **3. Marcações / agenda** | PARCIAL | `apps/appointments`: `Appointment`, estados, sobreposição; `AppointmentService` | Agenda, calendário, lista, formulários; `/appointments/*` | CRUD, `today`, `doctor`, `calendar`, `confirm/start/finish` | `test_appointments.py` (~10) | **Cancelamento: API `POST …/cancel/`**; **sem acção na UI** | v1.3.1: botão cancelar com motivo; receção já tem permissão `appointments.cancel` |
| **4. Fila de espera** | CONCLUÍDO | `WaitingQueue` ligada a check-in; prioridade; assign-to-doctor → `EM_ESPERA` | `WaitingQueuePage`, `QueueTable`, KPIs receção | Ver receção + fila médica `appointments/queue` | Coberto em receção + appointments | Dupla fila (receção vs médico) — por desenho | Documentar SOP: receção vs consultório |
| **5. Consultas (workflow)** | PARCIAL | Workflow completo no backend; integração receção | Páginas consulta activa `/consultations/:id`, fila médica | `start`, `finish`, `confirm`, estados | Sim | UI cancelamento ausente; edição pós-conclusão não regulada na UI | Fechar política de edição com direcção clínica |
| **6. Prontuário clínico (PCE)** | CONCLUÍDO | SOAP, diagnósticos, pedidos lab/img, seguimento; `ClinicalRecordService`; permissões `appointments.clinical*` | Separadores PCE, diagnósticos, pedidos lab/img | `GET …/clinical/`, POST diagnoses, laboratory, imaging, follow-up | `test_clinical_record.py` (~15) | CID-10 texto livre | Catálogo CID opcional fase 2 |
| **7. Sinais vitais** | PARCIAL | **Consulta:** `SinaisVitais` + `POST …/vital-signs/`; **Triagem:** PA no check-in receção | `SinaisVitaisForm` (consulta); triagem no wizard receção | Dois pontos de captura | Testes PCE + triagem receção | Sem módulo enfermagem; vitais não unificados no prontuário de triagem | v1.4: consolidar enfermagem/triagem |
| **8. Enfermagem** | PARCIAL | Role `ENFERMEIRO` em `UserRole` com permissões mínimas; **sem app `nursing`** | Sem `features/nursing`; triagem sob **receção** | N/A dedicado | Testes RBAC pontuais | Clínica não listou perfil Enfermeiro; procedimentos de enfermagem **não registados** | Tratar triagem como extensão da receção até v1.4; não activar `ENFERMEIRO` em produção |
| **9. Laboratório** | CONCLUÍDO | `PedidoLaboratorial`, resultados, anexos, validação/publicação; integração consulta | `features/laboratory` + `results` | `/laboratory/*`, `/laboratory/results/*` | `test_laboratory.py`, `test_laboratory_results.py` | Preço no `TipoExameLaboratorio` **ausente**; faturação **manual** via `Servico` | Alinhar tipos de exame ↔ catálogo CSV; opcional auto-linha na fatura |
| **10. Ecografia / imagiologia** | PARCIAL | `PedidoImagiologia` no PCE; `POST …/imaging/` | `PedidosImagiologia.tsx` (mensagem integração futura) | Pedido na consulta | Teste PCE imaging | Sem agenda, laudo, sala, fila; sem faturação automática | v1.5 módulo imagiologia |
| **11. Maternidade e parteira** | AUSENTE | Apenas consulta GO genérica + histórico paciente | N/A | N/A | N/A | Sem ficha gestante, parto, RN, parteira | v1.8 SRS; até lá usar consultas + catálogo |
| **12. Cirurgia** | AUSENTE | Evento histórico `CIRURGIA` no paciente; sem OT/bloco | N/A | N/A | N/A | Sem equipa, materiais, agenda cirúrgica | v1.7 SRS |
| **13. Catálogo de serviços** | PARCIAL | `billing.Servico` (código, categoria, preço); `import_servico_catalog`; Sprint 15 CSV | `/billing/services` | `/api/v1/billing/services/` | `test_billing.py` | `Departamento` **não ligado** a `Servico`; preços lab/eco não sincronizados com settings | Importar preçário real; modelar dept. analítico se relatórios exigirem |
| **14. Faturação** | PARCIAL | Orçamentos, faturas, itens `Servico`; `BillingService` + auditoria | Dashboard, faturas, orçamentos | `/billing/quotes`, `/invoices` | Sim | Sem geração automática a partir de lab/eco/procedimentos; **acesso receção bloqueado** | Dar `billing.*` à receção; fluxo único balcão |
| **15. Pagamentos** | CONCLUÍDO | `Pagamento`, confirmação, métodos FCFA; integração `finance` | `/billing/payments` | `/billing/payments/`, `confirm` | `test_billing.py` + finance | Mesmo bloqueio RBAC receção | Incluir permissões na receção |
| **16. Recibos** | CONCLUÍDO | `Recibo` imutável, numeração; ligado a pagamento | `/billing/receipts`, preview impressão | `/billing/receipts/` | Sim | Impressão nem sempre ligada ao ecrã | v1.3.1 impressões |
| **17. Medicamentos (urgência / uso interno)** | AUSENTE | `MedicamentoPrescrito` em prescrições médicas; **sem stock, validade, consumo** | Formulário prescrição | `/api/v1/prescriptions/` | `test_doctors.py` | Não distingue urgência vs ambulatorial; sem inventário interno | v1.6: stock mínimo urgência (não farmácia comercial) |
| **18. Materiais clínicos** | AUSENTE | Linhas `OUTRO`/`PROCEDIMENTO` no catálogo apenas | N/A | N/A | N/A | Sem registo de consumo em procedimentos/cirurgia | Incluir no SRS materiais + cirurgia/enfermagem |
| **19. Relatórios** | PARCIAL | `apps/reports`: PDF/Excel/CSV; `servicos_vendidos`; dashboards | `features/reports` | `/reports/*`, `/dashboard/executive/` | `test_reports.py` (~40) | **Sem receita por departamento**; sem relatório “urgências consumo” | Extender dimensões ou aceitar por categoria `Servico` |
| **20. Permissões RBAC** | PARCIAL | `seed_rbac`, `ModulePermission`, mixins por app | `navigation.ts`, `PermissionRoute`, guards | `/users/permissions/` | Múltiplos módulos | **`RECECIONISTA` sem billing**; roles extra `ENFERMEIRO`, `FINANCEIRO` no código; perfil clínica = 5 utilizadores | Reconfigurar seed: receção=faturação; desactivar FINANCEIRO; não criar novos perfis |
| **Internamento (camas / quartos)** | NÃO APLICÁVEL | Categoria `INTERNAMENTO` existe só em `Servico` | N/A | N/A | N/A | Clínica **não possui** internamento | Não implementar; remover linhas de diária do catálogo em produção se não usadas |
| **Farmácia comercial** | NÃO APLICÁVEL | Sem venda livre; prescrição ≠ dispensação comercial | N/A | N/A | N/A | Clínica **não possui** farmácia comercial | v1.6 apenas stock interno urgência, não POS farmácia |
| **Caixa separado da Receção** | NÃO APLICÁVEL | Módulo `finance` com `Caixa` existe tecnicamente | `/finance/cash` (Director) | `/api/v1/finance/cash-registers/` | `test_finance.py` | Organização clínica: **toda cobrança na receção** | Usar billing na receção; restringir finance/cash à direcção administrativa ou simplificar |

---

## 3. Mapa rápido backend ↔ frontend

| App Django | Frontend | Prefixo API |
|------------|----------|-------------|
| `patients` | `features/patients` | `/api/v1/patients/` |
| `reception` | `features/reception` | `/api/v1/reception/` |
| `appointments` (+ PCE) | `features/appointments` | `/api/v1/appointments/` |
| `laboratory` | `features/laboratory` | `/api/v1/laboratory/` |
| `doctors` | `features/doctors` | `/api/v1/prescriptions/`, treatments, etc. |
| `billing` | `features/billing` | `/api/v1/billing/` |
| `finance` | `features/finance` | `/api/v1/finance/` |
| `reports` | `features/reports` | `/api/v1/reports/` |
| `settings` | `features/settings` | `/api/v1/settings/` |
| `users` / `authentication` | auth + users | `/api/v1/auth/`, `/api/v1/users/` |

**Inexistentes:** `nursing`, `pharmacy`, `surgery`, `maternity`, `imaging`, `inventory`.

---

## 4. Resumo quantitativo

| Métrica | Valor |
|---------|------:|
| **Total de funcionalidades auditadas** | **23** |
| **CONCLUÍDO** | **6** |
| **PARCIAL** | **10** |
| **AUSENTE** | **4** |
| **NÃO APLICÁVEL** | **3** |

- **Linhas 1–20:** áreas obrigatórias da auditoria (20 linhas).  
- **Linhas 21–23:** declarações explícitas de não aplicabilidade (internamento, farmácia comercial, caixa separado).

### Distribuição das 20 áreas obrigatórias (linhas 1–20)

| Estado | Qtd | Áreas (#) |
|--------|----:|-----------|
| CONCLUÍDO | 6 | 2 Pacientes, 4 Fila, 6 PCE, 9 Laboratório, 15 Pagamentos, 16 Recibos |
| PARCIAL | 10 | 1 Receção, 3 Marcações, 5 Consultas, 7 Sinais vitais, 8 Enfermagem, 10 Ecografia, 13 Catálogo, 14 Faturação, 19 Relatórios, 20 RBAC |
| AUSENTE | 4 | 11 Maternidade, 12 Cirurgia, 17 Medicamentos urgência, 18 Materiais clínicos |

*Nota: Pagamentos e Recibos estão tecnicamente concluídos no módulo `billing`, mas o acesso pela Receção permanece parcial por RBAC — reflectido nas linhas 1, 14 e 20.*

---

## 5. Problemas críticos

1. **Desalinhamento operacional Receção ↔ Faturação:** a clínica confirma que toda a cobrança é na receção, mas `DEFAULT_ROLE_PERMISSIONS[RECECIONISTA]` **não inclui** `billing.view/create/payment/receipt`; o menu da receção **não expõe** `/billing`. Risco de go-live: impossível cobrar no balcão sem alteração de permissões ou uso exclusivo do Director.

2. **Medicamentos e materiais de urgência sem inventário:** prescrição médica existe; **não há** stock, validade, consumo nem ligação a procedimentos — requisito clínico confirmado **não coberto**.

3. **Maternidade e cirurgia:** áreas presentes na clínica física **sem** módulos, fluxos ou registos clínicos — apenas catálogo/preços de referência.

4. **Perfis no código vs. clínica:** existem `ENFERMEIRO` e `FINANCEIRO` no RBAC; a clínica define **5 perfis** e pede para não criar novos — risco de confusão e permissões indevidas se seeds não forem ajustados.

5. **Módulo `finance`/caixa técnico** coexistindo com regra “sem caixa separado”: Director pode operar caixa distinto do fluxo de receção — risco de dupla contabilidade operacional.

---

## 6. Problemas não críticos

- Cancelamento de consulta sem UI (API pronta).
- Impressões (fatura, recibo, receita, lab) parcialmente desligadas dos ecrãs.
- Ecografia: pedidos PCE sem módulo de laudo/agenda.
- Laboratório: preços só em `Servico`, não em `TipoExameLaboratorio`.
- Relatórios sem dimensão departamento.
- Notificação lab→médico (Celery stub).
- Recuperação de palavra-passe ausente.
- Categoria catálogo `INTERNAMENTO` irrelevante para esta clínica (manter inactiva).

---

## 7. Recomendação para implementação

### Fase imediata (sem novos módulos — alinhamento clínica)

1. **RBAC e UX da Receção:** conceder à role `RECECIONISTA` permissões `billing.view`, `billing.create`, `billing.payment`, `billing.receipt`, `billing.quote` (e opcionalmente `patients.view` já existe); adicionar secção **Faturação** ao menu receção; validar com UAT o fluxo paciente → triagem → fila → consulta → **fatura → pagamento → recibo** no mesmo perfil.

2. **Preçário:** importar `data/clinic/catalogo_servicos_sauvida.csv` (valores reais) e desactivar linhas `INTERNAMENTO` não usadas.

3. **Governança de perfis:** manter apenas Admin, Director, Médico, Receção, Lab em produção; **não atribuir** `ENFERMEIRO`/`FINANCEIRO`; documentar que Director usa relatórios/finance administrativo, não um balcão paralelo.

4. **v1.3.1:** cancelamento UI, impressões, notificação lab acordada.

### Fase seguinte (SRS antes de código)

| Ordem | Versão | Conteúdo |
|------:|--------|----------|
| 1 | v1.4 | Enfermagem/triagem unificada (sem novo perfil: extensão receção ou permissões no mesmo utilizador) |
| 2 | v1.5 | Ecografia + catálogo lab/imunologia |
| 3 | v1.6 | **Stock urgência** (medicamentos/materiais internos — não farmácia comercial) |
| 4 | v1.7 | Cirurgia |
| 5 | v1.8 | Maternidade/parteira |

### O que não fazer

- Internamento, farmácia comercial, novos perfis RBAC nesta fase.
- Implementar cirurgia/maternidade/farmácia completa antes de SRS assinado pela direcção.

---

## 8. Documentos relacionados

- `docs/SPRINT15/FLUXOS_REAIS_VALIDADOS.md`
- `docs/SPRINT15/VERIFICACAO_MATRIZ_AREAS.md`
- `docs/SPRINT15/LACUNAS_E_PRIORIDADES.md`
- `docs/AUDITORIA_PRE_SPRINT14.md`
- `backend/apps/users/management/commands/seed_rbac.py`
- `frontend/src/constants/navigation.ts`

---

*Auditoria estática ao repositório; validação em runtime (Docker, UAT) recomendada antes do go-live.*
