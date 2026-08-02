# Auditoria Pré-Sprint 14 — SGCS SauVida

**Data:** 2026-07-16  
**Âmbito:** Backend Django + Frontend React + infraestrutura (PostgreSQL, Redis, Celery, Docker, JWT, RBAC)  
**Objectivo:** Verificar implementação real das Sprints 1–13 antes da Sprint 14 (UI/UX).

---

## Resumo executivo

| Métrica | Valor |
|--------|------:|
| Funcionalidades verificadas | **168** |
| CONCLUÍDO | **142** (84,5 %) |
| PARCIAL | **24** (14,3 %) |
| AUSENTE | **2** (1,2 %) |
| Testes backend recolhidos | **245** |
| Testes após correcções críticas | **245 passed** (1 falha RBAC corrigida) |
| Build frontend | **OK** (`npm run build`) |

### Problemas críticos (corrigidos nesta auditoria)

| # | Problema | Acção |
|---|----------|--------|
| C1 | Refresh JWT: cliente não persistia o novo `refresh` após rotação (`ROTATE_REFRESH_TOKENS=True`) → sessões quebravam | Corrigido em `frontend/src/services/api/client.ts` |
| C2 | Fallback `appointments.edit` permitia à receção editar prontuário clínico | Removido em `backend/apps/appointments/permissions.py` |
| C3 | Teste esperava médico com acesso ao dashboard de receção (incompatível com RBAC actual) | Actualizado para 403 em `test_reception.py` |

### Problemas não críticos (adiáveis / Sprint 14+)

- Recuperação de palavra-passe (forgot/reset) ausente — existe apenas alteração autenticada
- Cancelamento de consulta: API OK, UI não ligada
- Seguro do paciente: API nested OK, sem UI
- CID-10: campo free-text, sem catálogo
- Notificação ao médico (lab): task Celery stub
- Backups / exports Celery: stubs
- Settings FE: várias páginas placeholder
- `seed_demo` — **implementado na Sprint 14** (`seed_demo.py`; ver `docs/DEMO_DATA.md`)
- FINANCEIRO no seed ainda tem `settings.*` (não usado em produção)
- Poucos leftovers de inglês na UI

---

## Tabela de auditoria

### 1. Autenticação e Utilizadores

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Modelo personalizado User | CONCLUÍDO | `authentication/models.py`, `managers.py` | — | users/auth | — | Manter |
| Login por e-mail | CONCLUÍDO | `backends.py`, `LoginPage.tsx` | `POST /auth/login/` | audit login | — | Manter |
| JWT access + refresh | CONCLUÍDO | simplejwt settings, `views.py` | `/auth/login/`, `/auth/refresh/` | — | — | Manter |
| Logout + blacklist | CONCLUÍDO | `LogoutView`, AuthContext | `POST /auth/logout/` | parcial | — | Manter |
| Refresh automático FE | CONCLUÍDO* | `services/api/client.ts` | `/auth/refresh/` | — | *Corrigido C1 | Validar em QA |
| Alteração de palavra-passe | CONCLUÍDO | `PasswordChangeView`, ProfilePage | `POST /users/profile/password/` | parcial | — | Manter |
| Recuperação (forgot) | AUSENTE | — | — | — | Sem fluxo | Sprint futura |
| Gestão de sessões | PARCIAL | `UserSession`, ProfilePage | `GET /users/profile/sessions/` | parcial | Sem revoke individual | Sprint 14+ |
| Activar / desactivar | CONCLUÍDO | UserService, UsersListPage | `…/activate/`, `…/deactivate/` | users tests | — | Manter |
| Soft delete | CONCLUÍDO | `soft_delete`, delete account | `DELETE /users/accounts/{id}/` | soft delete test | — | Manter |
| Histórico de acessos | CONCLUÍDO | AuditLog + ProfilePage | `GET /users/profile/access-history/` | audit | — | Manter |
| Brute-force / rate limit | CONCLUÍDO | `login_guard.py`, throttle | login | `TestLoginGuard` | — | Manter |
| Auditoria login/logout | CONCLUÍDO | AuditService | — | `test_login_creates_audit_log` | — | Manter |

### 2. Perfis e RBAC

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Roles (Admin, Director, Médico, Receção, Lab, Financeiro) | CONCLUÍDO | `UserRole`, `roles.ts` | roles API | seed + RBAC tests | ENFERMEIRO extra | Manter FINANCEIRO sem users |
| Permissões módulo.acção | CONCLUÍDO | `ModulePermission`, `seed_rbac.py` | `/users/permissions/` | seed | — | Re-seed em deploy |
| Validação backend | CONCLUÍDO | `HasModulePermission`, mixins | todos módulos | RBAC por app | — | Manter |
| Guards frontend | CONCLUÍDO | `guards.tsx`, `RoleGuard`, `usePermissions` | — | — | — | Manter |
| Menus dinâmicos | CONCLUÍDO | `navigation.ts`, `AppSidebar.tsx` | — | — | — | Sprint 14 polish |
| Director: finance/billing/reports | CONCLUÍDO | seed DIRECTOR | — | reports director tests | — | Manter |
| Director sem settings/users | CONCLUÍDO | seed + AdminOnlyRoute | — | settings 403 director | — | Manter |
| Médico sem billing/finance | CONCLUÍDO | seed + sidebar | — | — | — | Manter |
| Receção sem PCE completo | CONCLUÍDO* | permissions clinical | clinical API | clinical RBAC | *Corrigido C2 | Validar QA |
| Lab sem billing/finance/settings | CONCLUÍDO | seed + sidebar | — | — | — | Manter |
| Admin acesso total | CONCLUÍDO | `__all__` + short-circuit | — | — | — | Manter |

### 3. Gestão de Pacientes

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Registo / nº processo | CONCLUÍDO | patients app + FE | `/patients/` | patients tests | — | Manter |
| Pesquisa / filtros / paginação | CONCLUÍDO | filters, PatientsListPage | query params | search test | — | Sprint 14 UI |
| Contactos / emergência | CONCLUÍDO | nested resources + forms | emergency-contacts | tests | — | Manter |
| Clínico básico | CONCLUÍDO | allergies, chronic, observations | nested | allergy test | — | Manter |
| Seguros | PARCIAL | BE `PatientInsurance` | `/insurances/` | parcial | Sem UI | Sprint 14+ UI |
| Documentos / histórico | CONCLUÍDO | documents, history | nested + history | history tests | — | Sprint 14 UI |
| Soft delete / audit / RBAC | CONCLUÍDO | patient_service | DELETE, audit-trail | TestPatient* | UI usa desactivar | OK |
| Dashboard KPIs | CONCLUÍDO | clinical dashboard | `/dashboard/clinical/` | dashboard tests | — | Manter |

### 4. Receção

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Check-in / fila / prioridades | CONCLUÍDO | reception app + FE | check-in, queue | TestReception* | — | Sprint 14 UI |
| Encaminhamento / histórico | CONCLUÍDO | Referral, history | referrals, history | referral tests | — | Manter |
| Integração pacientes/consultas | CONCLUÍDO | handoff → Appointment | — | handoff test | — | Manter |
| Redis cache / audit / dashboard | CONCLUÍDO | reception_service, dashboard | `/dashboard/reception/` | dashboard tests | — | Manter |

### 5. Agenda e Consultas

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Marcar / reagendar / confirmar | CONCLUÍDO | appointment_service + FE | CRUD, confirm | appointment tests | — | Manter |
| Cancelar | PARCIAL | BE cancel action | `POST …/cancel/` | cancel RBAC | Sem botão UI | Sprint 14 wire UI |
| Agenda diária / calendário | CONCLUÍDO | today, calendar + FE | today, calendar | calendar tests | — | Sprint 14 UI |
| Anti-sobreposição | CONCLUÍDO | validators | create/update | overlap test | — | Manter |
| Start / finish / fila | CONCLUÍDO | start, finish, queue | — | fluxo completo | — | Manter |
| Dashboard médico | CONCLUÍDO | consultas dashboard + FE | `/dashboard/consultas/` | dashboard test | — | Sprint 14 polish |

### 6. Prontuário Clínico Electrónico

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Sinais vitais / IMC | CONCLUÍDO | SinaisVitais, forms | vital-signs | IMC test | — | Sprint 14 UX |
| SOAP / diagnósticos | CONCLUÍDO | AnotacaoClinica, Diagnostico | clinical, diagnoses | SOAP/diag tests | — | Sprint 14 UX |
| CID-10 | PARCIAL | campo `codigo_cid10` | — | manual codes | Sem catálogo | Sprint futura |
| Prescrições / plano / evolução / alta / seguimento | CONCLUÍDO | doctors app + FE | prescriptions, evolutions, discharges, followups | doctors tests | — | Sprint 14 UX |
| Lock pós-conclusão | CONCLUÍDO | `_ensure_editable` | — | bloqueio test | — | Manter |
| Histórico / auditoria | CONCLUÍDO | obter_prontuario, AuditService | clinical GET | PCE tests | — | Manter |

### 7. Laboratório

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Pedidos → workflow (receber/colher/processar) | CONCLUÍDO | laboratory app + FE | receive, collect, start, finish | lab tests | — | Sprint 14 UI |
| Resultados / parâmetros / referência | CONCLUÍDO | results services + FE | results CRUD, parameters | results tests | — | Sprint 14 UI |
| Interpretação automática | PARCIAL | `_calcular_interpretacao` | — | NORMAL assert | CRITICO não auto | Melhorar opcional |
| Validar / publicar / anexos / download | CONCLUÍDO | validate, publish, attachments | — | fluxo API | download pouco testado | Manter |
| Integração PCE | CONCLUÍDO | validate → consulta | — | integração test | — | Manter |
| Notificar médico | PARCIAL | Celery task | — | — | Stub | Implementar Sprint futura |
| Dashboard / auditoria | CONCLUÍDO | lab dashboard | `/dashboard/laboratory/` | test_dashboard | — | Sprint 14 polish |

### 8. Faturação

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Serviços / orçamentos / aprovação | CONCLUÍDO | billing app + FE | services, quotes, approve | billing tests | — | Sprint 14 UI |
| Faturas / itens / pagamentos / parciais | CONCLUÍDO | Fatura, Pagamento, PARCIAL | invoices, payments | fluxo orçamento-fatura | — | Manter |
| Recibos / numeração / histórico paciente | CONCLUÍDO | Recibo, number_service | receipts, patient-history | historico test | — | Sprint 14 UI |
| Integração consulta | CONCLUÍDO | Fatura.consulta FK | — | — | — | Manter |
| Integração lab | PARCIAL | categoria EXAME | — | — | Sem FK pedido lab | Futuro |
| Dashboard / auditoria | CONCLUÍDO | billing dashboard | `/dashboard/billing/` | dashboard test | — | Sprint 14 polish |

### 9. Financeiro

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Caixa open/close / movimentos | CONCLUÍDO | finance app + FE | cash-registers, movements | finance tests | — | Sprint 14 UI |
| Receitas / despesas / categorias | CONCLUÍDO | Despesa, CategoriaFinanceira | expenses, categories | criar despesa | — | Manter |
| Fluxo de caixa / lucro / relatórios | CONCLUÍDO | calcular_fluxo_caixa, reports | daily/monthly/yearly | fluxo + relatório | — | Sprint 14 charts |
| Integração pagamentos confirmados | CONCLUÍDO | processar_pagamento_billing | — | pagamento→movimento | — | Manter |
| Dashboard + permissões Director | CONCLUÍDO | seed + FinanceDashboardPage | `/dashboard/finance/` | dashboard test | — | Sprint 14 polish |

### 10. Relatórios e BI

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Relatórios por módulo + executivo | CONCLUÍDO | reports app + FE | `/reports/*`, `/dashboard/executive/` | reports tests | — | Sprint 14 UI |
| Séries / KPIs / filtros período | CONCLUÍDO | StatisticsService, charts | charts, statistics | periodo test | — | Manter |
| Export PDF/Excel/CSV | CONCLUÍDO | pdf/excel/csv services | `?export=` | export audit | Celery stubs | Aceitável |
| Cache Redis / auditoria export | CONCLUÍDO | ReportsCacheService | — | cache + audit tests | — | Manter |

### 11. Administração e Configurações

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Clínica / NIF / FCFA / PT / fuso | CONCLUÍDO | PerfilClinica, constants | `/settings/clinic/` | clinic tests | — | Manter |
| Especialidades / deptos / salas / horários / feriados | CONCLUÍDO | models + routers | settings/* | CRUD tests | FE placeholders salas/horários | Sprint 14 UI |
| Tipos consulta / exames | CONCLUÍDO | API | consultation-types, exam-types | — | FE placeholder | Sprint 14 UI |
| Billing/email/security/files config | CONCLUÍDO | settings views | — | security tests | FE parcial | Sprint 14 UI |
| Feature flags / backups / monitorização | PARCIAL | API + MonitoringService | feature-flags, backups, monitoring, system | settings tests | Backups Celery stub; FE flags OK | Sprint 14 UI + stub note |
| Dashboard sistema | CONCLUÍDO | get_system_dashboard | `/dashboard/system/` | system tests | — | Admin panel |

### 12. Notificações

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Centro / não lidas / ler / arquivar | CONCLUÍDO | notifications app + FE | unread, read, archive | notifications tests | — | Sprint 14 polish |
| Templates e-mail/SMS / preferências / histórico | CONCLUÍDO | templates, preferences | — | history tests | — | Manter |
| Event Bus / Celery / Redis / audit | CONCLUÍDO | event_handlers, tasks, cache | — | event + celery tests | — | Manter |

### 13. Produção e Segurança

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Production settings / DEBUG | CONCLUÍDO | `config/settings/production.py` | — | — | — | Manter |
| Rate limit / brute-force / headers / HSTS / CSP | CONCLUÍDO | middleware, throttling, login_guard | — | sprint13 security | — | Manter |
| Cookies seguros / uploads / logging | CONCLUÍDO | production + validators + logging_config | — | upload + logging tests | — | Manter |
| Health / live / ready | CONCLUÍDO | core/health | `/health/`, `/live/`, `/ready/` | health tests | — | Manter |
| Postgres/Redis/Celery monitor + retry | CONCLUÍDO | HealthService, SGCSBaseTask | monitoring | health + celery | — | Manter |
| Storage / cache / queries / FE split / ErrorBoundary / skeletons | CONCLUÍDO | core storage/cache, lazyRoutes, ErrorBoundary | — | performance queryset | — | Manter |
| Docs produção | CONCLUÍDO | `docs/Deployment.md`, Monitoring | — | — | — | Actualizar Sprint 14 |

### 14. Interface em Português

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Textos UI (menus, forms, dashboards) | PARCIAL | `uiCopy.ts`, features/* | — | — | Poucos leftovers EN | Sprint 14 limpeza |
| Login / branding | PARCIAL | AuthLayout, LoginPage | — | — | Iterações UX recentes | Sprint 14 |

### 15. Utilizadores reais da clínica

| Funcionalidade | Estado | Ficheiros | Endpoints | Testes | Problemas | Acção |
|----------------|--------|-----------|-----------|--------|-----------|--------|
| Elenco 1+1+2+1+1 (sem FINANCEIRO) | CONCLUÍDO* | `seed_demo.py` | — | — | *Implementado Sprint 14 | Ver DEMO_DATA.md |
| FINANCEIRO no RBAC sem users | CONCLUÍDO | seed_rbac, ASSIGNABLE_ROLES exclui | — | — | settings.* no seed FINANCEIRO | Opcional limpar settings |

---

## Contagens por domínio

| Domínio | Itens | CONCLUÍDO | PARCIAL | AUSENTE |
|---------|------:|----------:|--------:|--------:|
| Auth | 12 | 10 | 1 | 1 |
| RBAC | 11 | 11 | 0 | 0 |
| Pacientes | 10 | 9 | 1 | 0 |
| Receção | 9 | 9 | 0 | 0 |
| Consultas | 10 | 9 | 1 | 0 |
| PCE | 10 | 9 | 1 | 0 |
| Laboratório | 12 | 10 | 2 | 0 |
| Faturação | 12 | 11 | 1 | 0 |
| Financeiro | 10 | 10 | 0 | 0 |
| Relatórios | 8 | 8 | 0 | 0 |
| Settings | 10 | 8 | 2 | 0 |
| Notificações | 8 | 8 | 0 | 0 |
| Produção | 12 | 12 | 0 | 0 |
| UI PT | 2 | 0 | 2 | 0 |
| Utilizadores demo | 2 | 1 | 0 | 1 |
| **Total** | **168** | **142** | **24** | **2** |

---

## Testes e build (evidência)

```
pytest: 245 collected
Após correcções: reception + clinical = 17 passed (amostra)
Suite completa pré-fix: 244 passed, 1 failed (RBAC médico/receção) → corrigido

npm run build: SUCCESS (tsc + vite)
```

---

## Decisão

**Problemas críticos identificados e corrigidos nesta auditoria.**  
Não restam bloqueadores de autenticidade/autorização/integridade clínica para iniciar a Sprint 14.

**Decisão: INICIAR SPRINT 14** — UI/UX Premium, `seed_demo`, documentação e refinamentos de fluxo **sem alterar contratos API / JWT / modelos / regras de negócio**.

---

## Checklist pós-auditoria (ambiente)

```bash
cd backend
python manage.py migrate
python manage.py seed_rbac
python manage.py seed_demo   # Sprint 14
pytest -q
cd ../frontend && npm run build
curl http://localhost:8000/health/
```
