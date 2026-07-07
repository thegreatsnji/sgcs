# SGCS — Sistema de Gestão Clínica SauVida

Sistema de gestão clínica para a SauVida, desenvolvido com arquitetura moderna full-stack.

## Stack tecnológica

| Camada | Tecnologias |
|--------|-------------|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, React Hook Form, Zod, Axios |
| **Backend** | Python, Django 5, Django REST Framework |
| **Autenticação** | JWT (SimpleJWT) com refresh token e blacklist |
| **Base de dados** | PostgreSQL 16 |
| **Documentação API** | OpenAPI / Swagger (drf-spectacular) |
| **Infraestrutura** | Docker, Docker Compose |

## Estrutura do projeto

```
SGCS/
├── backend/
│   ├── apps/              # Módulos Django por domínio
│   ├── core/              # Utilitários transversais da API
│   │   ├── config/        # Cache, storage, feature flags, enums
│   │   ├── events/        # Event bus pub/sub
│   │   └── health/        # Probes /health, /live, /ready
│   └── config/            # Configuração Django + Celery
├── frontend/
│   └── src/
│       ├── components/    # UI legado (mantido para compatibilidade)
│       ├── design-system/ # Componentes base empresariais
│       ├── features/      # Estrutura por domínio (migração gradual)
│       ├── constants/     # Constantes da aplicação
│       ├── services/      # Serviços API por módulo
│       ├── theme/         # Tema visual
│       └── types/         # Tipos TypeScript por domínio
├── database/              # Scripts PostgreSQL
├── docker/                # Dockerfiles
├── docs/                  # Documentação (incl. Arquitetura.md)
├── scripts/               # Scripts de automação
├── docker-compose.yml
├── .env.example
└── README.md
```

Consulte [docs/Arquitetura.md](docs/Arquitetura.md) para a descrição detalhada da arquitetura.

## Pré-requisitos

- [Docker](https://www.docker.com/) e Docker Compose
- [Python](https://www.python.org/) 3.11+ (desenvolvimento local)
- [Node.js](https://nodejs.org/) 20+ e npm

## Instalação rápida (Docker)

1. Clone o repositório e entre na pasta do projeto:

```bash
cd SGCS
```

2. Crie o ficheiro de ambiente:

```bash
cp .env.example .env
```

3. Inicie todos os serviços:

```bash
docker compose up --build
```

O entrypoint do backend executa automaticamente `migrate` e `seed_rbac` (permissões RBAC incluindo `patients.*`).

4. Crie um superutilizador (num terminal separado):

```bash
docker compose exec backend python manage.py create_superuser_dev
```

> **Nota:** O script está na raiz do projeto. Alternativa dentro do contentor:
> `docker compose exec backend python manage.py create_superuser_dev`

### URLs de desenvolvimento

| Serviço | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/v1 |
| Health | http://localhost:8000/health/ |
| Liveness | http://localhost:8000/live/ |
| Readiness | http://localhost:8000/ready/ |
| Swagger UI | http://localhost:8000/api/docs/ |
| ReDoc | http://localhost:8000/api/redoc/ |
| Django Admin | http://localhost:8000/admin/ |

### Credenciais padrão (desenvolvimento)

| Campo | Valor |
|-------|-------|
| E-mail | `admin@sauvida.ao` |
| Palavra-passe | `Admin@12345` |

## Instalação local (sem Docker completo)

### 1. Variáveis de ambiente

```bash
cp .env.example .env
```

### 2. Base de dados PostgreSQL

Inicie apenas o PostgreSQL via Docker:

```bash
docker compose up -d db
```

### 3. Backend

```bash
python -m venv backend/.venv

# Windows
backend\.venv\Scripts\activate

# Linux/macOS
source backend/.venv/bin/activate

pip install -r backend/requirements/development.txt
cd backend
python manage.py migrate
cd ..
python scripts/create_superuser.py
cd backend
python manage.py runserver
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

### Script automatizado (Windows)

```bash
scripts\setup-dev.bat
```

## Infraestrutura Docker

| Serviço | Função |
|---------|--------|
| `db` | PostgreSQL 16 |
| `redis` | Cache Django + broker Celery |
| `backend` | API Django/DRF |
| `celery-worker` | Processamento assíncrono |
| `celery-beat` | Tarefas agendadas (ex.: `sgcs.ping`) |
| `frontend` | SPA React (Vite) |

## Endpoints de saúde

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health/` | Estado geral da aplicação |
| `GET` | `/live/` | Liveness probe (processo ativo) |
| `GET` | `/ready/` | Readiness probe (DB + cache) |

## Endpoints de autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/auth/login/` | Iniciar sessão (JWT) |
| `POST` | `/api/v1/auth/refresh/` | Renovar access token |
| `POST` | `/api/v1/auth/logout/` | Terminar sessão (blacklist) |
| `GET` | `/api/v1/auth/me/` | Utilizador autenticado |
| `POST` | `/api/v1/auth/register/` | Registo de utilizador |

## Módulo de Pacientes (Sprint 4)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/v1/patients/` | Listagem com pesquisa, filtros e paginação |
| `POST` | `/api/v1/patients/` | Criar paciente |
| `GET` | `/api/v1/patients/{id}/` | Detalhe do paciente |
| `PATCH` | `/api/v1/patients/{id}/` | Atualizar paciente |
| `DELETE` | `/api/v1/patients/{id}/` | Soft delete |
| `GET` | `/api/v1/patients/check-duplicate/` | Verificar duplicados |
| `GET` | `/api/v1/patients/{id}/audit-trail/` | Auditoria do paciente |
| `GET` | `/api/v1/dashboard/clinical/` | KPIs clínicos (requer `patients.view`) |

Documentação completa: [docs/Patients/](docs/Patients/README.md)

## Módulo de Receção (Sprint 5)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/v1/reception/check-in/` | Check-in de paciente (requer `reception.create`) |
| `GET` | `/api/v1/reception/queue/` | Fila de espera activa |
| `PATCH` | `/api/v1/reception/queue/{id}/` | Actualizar estado na fila |
| `POST` | `/api/v1/reception/assign-to-doctor/` | Encaminhar para médico |
| `GET` | `/api/v1/reception/history/` | Histórico de check-ins |
| `POST` | `/api/v1/reception/referrals/` | Encaminhamento geral (LAB/BILLING) |
| `GET` | `/api/v1/dashboard/reception/` | KPIs de receção (requer `reception.view`) |

### Rotas frontend — Receção

| Rota | Descrição |
|------|-----------|
| `/reception` | Painel de receção |
| `/reception/check-in` | Check-in de paciente |
| `/reception/queue` | Fila de espera |
| `/reception/referrals` | Encaminhamentos |

## Módulo de Consultas (Sprint 6 — Fase 1)

### Endpoints principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/v1/appointments/` | Listagem com filtros e paginação |
| `POST` | `/api/v1/appointments/` | Agendar consulta (`appointments.create`) |
| `GET` | `/api/v1/appointments/{id}/` | Detalhe da consulta |
| `PATCH` | `/api/v1/appointments/{id}/` | Reagendar / editar (`appointments.edit`) |
| `DELETE` | `/api/v1/appointments/{id}/` | Remover (`appointments.delete`) |
| `POST` | `/api/v1/appointments/{id}/confirm/` | Confirmar consulta |
| `POST` | `/api/v1/appointments/{id}/start/` | Iniciar consulta |
| `POST` | `/api/v1/appointments/{id}/finish/` | Concluir consulta |
| `POST` | `/api/v1/appointments/{id}/cancel/` | Cancelar (com motivo) |
| `GET` | `/api/v1/appointments/today/` | Consultas do dia |
| `GET` | `/api/v1/appointments/doctor/` | Agenda do médico |
| `GET` | `/api/v1/appointments/calendar/` | Vista de calendário |
| `GET` | `/api/v1/dashboard/consultas/` | KPIs de agenda e consultas |

### Endpoints legados (mantidos — compatibilidade)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/v1/appointments/queue/` | Fila médica (recepção → médico) |
| `PATCH` | `/api/v1/appointments/{id}/clinical/` | Actualizar dados clínicos (legado) |
| `POST` | `/api/v1/appointments/{id}/complete/` | Alias de `finish` |
| `GET` | `/api/v1/dashboard/consultations/` | Alias de `/dashboard/consultas/` |

### Prontuário Clínico Eletrónico — Sprint 6 Fase 2

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/v1/appointments/{id}/clinical/` | Prontuário completo (paciente + PCE) |
| `POST` | `/api/v1/appointments/{id}/vital-signs/` | Registar sinais vitais (IMC automático) |
| `POST` | `/api/v1/appointments/{id}/diagnoses/` | Adicionar diagnóstico CID-10 |
| `POST` | `/api/v1/appointments/{id}/laboratory/` | Pedido de laboratório |
| `POST` | `/api/v1/appointments/{id}/imaging/` | Pedido de imagiologia |
| `POST` | `/api/v1/appointments/{id}/follow-up/` | Agendar seguimento |

Permissões PCE: `appointments.clinical`, `.diagnosis`, `.request_lab`, `.request_imaging`, `.followup`

### Estados da consulta

`AGENDADA` · `CONFIRMADA` · `EM_ESPERA` · `EM_CONSULTA` · `CONCLUIDA` · `CANCELADA` · `FALTA`

### Permissões RBAC

`appointments.view` · `appointments.create` · `appointments.edit` · `appointments.delete` · `appointments.confirm` · `appointments.start` · `appointments.finish` · `appointments.cancel`

### Rotas frontend — Consultas (novas)

| Rota | Descrição |
|------|-----------|
| `/appointments` | Agenda médica / painel |
| `/appointments/calendar` | Calendário |
| `/appointments/list` | Lista de consultas |
| `/appointments/queue` | Fila médica |
| `/appointments/new` | Nova consulta |
| `/appointments/:id` | Detalhes |
| `/appointments/:id/edit` | Editar / reagendar |

### Rotas frontend — Consultas (legadas)

| Rota | Descrição |
|------|-----------|
| `/consultations` | Painel médico |
| `/consultations/queue` | Fila médica |
| `/consultations/history` | Histórico |
| `/consultations/:id` | Consulta activa / detalhe |

### Rotas frontend — Pacientes

| Rota | Descrição |
|------|-----------|
| `/patients` | Lista de pacientes |
| `/patients/new` | Novo paciente |
| `/patients/:id` | Resumo / detalhes |
| `/patients/:id/edit` | Editar |
| `/patients/:id/clinical` | Ficha clínica |
| `/patients/:id/documents` | Documentos |
| `/patients/:id/history` | Histórico e auditoria |

## Módulo de Laboratório (Sprint 7 — Fase 1)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/v1/laboratory/` | Listagem de pedidos |
| `GET` | `/api/v1/laboratory/pending/` | Pedidos pendentes |
| `GET` | `/api/v1/laboratory/today/` | Pedidos do dia |
| `GET` | `/api/v1/laboratory/{id}/` | Detalhe do pedido |
| `PATCH` | `/api/v1/laboratory/{id}/` | Actualizar observações/prioridade |
| `POST` | `/api/v1/laboratory/{id}/receive/` | Receber pedido |
| `POST` | `/api/v1/laboratory/{id}/collect/` | Registar colheita |
| `POST` | `/api/v1/laboratory/{id}/start/` | Iniciar processamento |
| `POST` | `/api/v1/laboratory/{id}/finish/` | Concluir exame |
| `GET` | `/api/v1/laboratory/collection-queue/` | Fila de colheitas |
| `GET` | `/api/v1/dashboard/laboratory/` | KPIs do laboratório |

Integração automática: pedidos emitidos na consulta (`POST /appointments/{id}/laboratory/`) criam `PedidoLaboratorial` no módulo Laboratório.

### Permissões RBAC

`laboratory.view` · `laboratory.edit` · `laboratory.receive` · `laboratory.collect` · `laboratory.process` · `laboratory.finish`

### Rotas frontend — Laboratório

| Rota | Descrição |
|------|-----------|
| `/laboratory` | Painel |
| `/laboratory/pending` | Pedidos pendentes |
| `/laboratory/today` | Pedidos do dia |
| `/laboratory/collection` | Fila de colheitas |
| `/laboratory/:id` | Detalhes do pedido |

## Módulo de Resultados Laboratoriais (Sprint 7 — Fase 2)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/v1/laboratory/results/` | Listagem de resultados |
| `GET` | `/api/v1/laboratory/results/{id}/` | Detalhe do resultado |
| `POST` | `/api/v1/laboratory/results/` | Criar resultado (com parâmetros) |
| `PATCH` | `/api/v1/laboratory/results/{id}/` | Editar resultado |
| `POST` | `/api/v1/laboratory/results/{id}/validate/` | Validar resultado |
| `POST` | `/api/v1/laboratory/results/{id}/publish/` | Publicar ao médico |
| `POST` | `/api/v1/laboratory/results/{id}/attachments/` | Anexar PDF/imagem |
| `GET` | `/api/v1/laboratory/results/{id}/download/` | Download de anexo |

Ao validar: actualiza pedido, consulta, prontuário clínico, dashboard, auditoria e event bus.

### Permissões RBAC (resultados)

`laboratory.results.view` · `laboratory.results.create` · `laboratory.results.edit` · `laboratory.results.validate` · `laboratory.results.publish` · `laboratory.results.download`

### Rotas frontend — Resultados

| Rota | Descrição |
|------|-----------|
| `/laboratory/results` | Painel de resultados |
| `/laboratory/results/history` | Histórico |
| `/laboratory/results/new` | Novo resultado |
| `/laboratory/results/:id` | Detalhes |
| `/laboratory/results/:id/edit` | Editar |

Prontuário clínico: separador **Resultados Laboratoriais** na consulta.

## Módulo de Faturação (Sprint 8 — Fase 1)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET/POST/PATCH/DELETE` | `/api/v1/billing/services/` | Catálogo de serviços |
| `GET/POST/PATCH` | `/api/v1/billing/quotes/` | Orçamentos |
| `POST` | `/api/v1/billing/quotes/{id}/approve/` | Aprovar orçamento |
| `GET/POST/PATCH` | `/api/v1/billing/invoices/` | Faturas |
| `GET/POST/PATCH` | `/api/v1/billing/payments/` | Pagamentos |
| `POST` | `/api/v1/billing/payments/{id}/confirm/` | Confirmar pagamento |
| `GET` | `/api/v1/billing/receipts/` | Recibos |
| `GET` | `/api/v1/billing/receipts/{id}/` | Detalhe do recibo |
| `GET` | `/api/v1/billing/patient-history/{patient_id}/` | Histórico financeiro |
| `GET` | `/api/v1/dashboard/billing/` | KPIs financeiros |

### Permissões RBAC (faturação)

`billing.view` · `billing.create` · `billing.edit` · `billing.delete` · `billing.payment` · `billing.receipt` · `billing.quote`

### Rotas frontend — Faturação

| Rota | Descrição |
|------|-----------|
| `/billing` | Painel financeiro |
| `/billing/services` | Serviços |
| `/billing/quotes` | Orçamentos |
| `/billing/invoices` | Faturas |
| `/billing/payments` | Pagamentos |
| `/billing/receipts` | Recibos |
| `/billing/history` | Histórico financeiro |

## Módulo Financeiro (Sprint 8 — Fase 2)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET/POST/PATCH` | `/api/v1/finance/cash-registers/` | Caixas |
| `POST` | `/api/v1/finance/cash-registers/{id}/open/` | Abrir caixa |
| `POST` | `/api/v1/finance/cash-registers/{id}/close/` | Fechar caixa |
| `GET` | `/api/v1/finance/movements/` | Movimentos financeiros |
| `GET/POST/PATCH` | `/api/v1/finance/expenses/` | Despesas |
| `POST` | `/api/v1/finance/expenses/{id}/approve/` | Aprovar despesa |
| `POST` | `/api/v1/finance/expenses/{id}/pay/` | Pagar despesa |
| `GET/POST/PATCH` | `/api/v1/finance/categories/` | Categorias financeiras |
| `GET` | `/api/v1/finance/reports/daily/` | Relatório diário |
| `GET` | `/api/v1/finance/reports/monthly/` | Relatório mensal |
| `GET` | `/api/v1/finance/reports/yearly/` | Relatório anual |
| `GET` | `/api/v1/dashboard/finance/` | KPIs financeiros |

### Permissões RBAC (financeiro)

`finance.view` · `finance.create` · `finance.edit` · `finance.delete` · `finance.cash` · `finance.expense` · `finance.report` · `finance.dashboard`

### Rotas frontend — Financeiro

| Rota | Descrição |
|------|-----------|
| `/finance` | Painel financeiro |
| `/finance/cash` | Caixas |
| `/finance/cash/:id` | Detalhe do caixa |
| `/finance/movements` | Movimentos |
| `/finance/expenses` | Despesas |
| `/finance/expenses/new` | Nova despesa |
| `/finance/reports` | Relatórios |

Integração automática: confirmação de pagamento em Billing cria `MovimentoFinanceiro` (ENTRADA), actualiza caixa, dashboard, cache Redis, auditoria e event bus (`finance.payment.received`).

## Módulo de Relatórios e BI (Sprint 9)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/v1/reports/patients/` | Relatório de pacientes |
| `GET` | `/api/v1/reports/appointments/` | Relatório de consultas |
| `GET` | `/api/v1/reports/reception/` | Relatório de receção |
| `GET` | `/api/v1/reports/laboratory/` | Relatório de laboratório |
| `GET` | `/api/v1/reports/billing/` | Relatório de faturação |
| `GET` | `/api/v1/reports/finance/` | Relatório financeiro |
| `GET` | `/api/v1/reports/charts/` | Séries temporais (gráficos) |
| `GET` | `/api/v1/reports/statistics/` | Estatísticas agregadas |
| `GET` | `/api/v1/dashboard/executive/` | Dashboard executivo |

Todos os relatórios suportam `?export=pdf|xlsx|csv` e filtros de período (`hoje`, `semana`, `mes`, `ano`, `personalizado`).

### Permissões RBAC (relatórios)

`reports.view` · `reports.export` · `reports.dashboard` · `reports.statistics`

### Rotas frontend — Relatórios

| Rota | Descrição |
|------|-----------|
| `/reports` | Painel BI |
| `/reports/patients` | Pacientes |
| `/reports/appointments` | Consultas |
| `/reports/laboratory` | Laboratório |
| `/reports/billing` | Faturação |
| `/reports/finance` | Financeiro |
| `/reports/executive` | Dashboard executivo |

## Módulo de Configurações (Sprint 10)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET/PATCH` | `/api/v1/settings/clinic/` | Dados da clínica |
| `GET/POST/PATCH/DELETE` | `/api/v1/settings/specialties/` | Especialidades médicas |
| `GET/POST/PATCH/DELETE` | `/api/v1/settings/departments/` | Departamentos |
| `GET/POST/PATCH/DELETE` | `/api/v1/settings/rooms/` | Consultórios/salas |
| `GET/POST/PATCH/DELETE` | `/api/v1/settings/working-hours/` | Horários |
| `GET/POST/PATCH/DELETE` | `/api/v1/settings/holidays/` | Feriados |
| `GET/POST/PATCH/DELETE` | `/api/v1/settings/consultation-types/` | Tipos de consulta |
| `GET/POST/PATCH/DELETE` | `/api/v1/settings/laboratory/exam-types/` | Tipos de exames |
| `GET/PATCH` | `/api/v1/settings/billing/` | Configuração faturação |
| `GET/PATCH` | `/api/v1/settings/email/` | SMTP |
| `POST` | `/api/v1/settings/email/test/` | Testar ligação |
| `GET/PATCH` | `/api/v1/settings/security/` | Segurança |
| `GET/PATCH` | `/api/v1/settings/feature-flags/` | Feature flags |
| `GET/POST` | `/api/v1/settings/backups/` | Backups |
| `GET` | `/api/v1/settings/monitoring/` | Monitorização |
| `GET` | `/api/v1/dashboard/system/` | Dashboard do sistema |

### Permissões RBAC (configurações)

`settings.view` · `settings.edit` · `settings.security` · `settings.backup` · `settings.system` · `settings.email` · `settings.featureflags`

### Rotas frontend — Configurações

| Rota | Descrição |
|------|-----------|
| `/settings` | Painel administrativo |
| `/settings/clinic` | Dados da clínica |
| `/settings/departments` | Departamentos |
| `/settings/specialties` | Especialidades |
| `/settings/security` | Segurança |
| `/settings/feature-flags` | Feature flags |
| `/settings/system` | Estado do sistema |

Documentação: `docs/Deployment.md`, `docs/SystemAdministration.md`

### API — Módulo Médico (Sprint 11)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET/POST/PATCH` | `/api/v1/prescriptions/` | Prescrições médicas |
| `POST` | `/api/v1/prescriptions/{id}/approve/` | Aprovar prescrição |
| `POST` | `/api/v1/prescriptions/{id}/finish/` | Concluir prescrição |
| `GET` | `/api/v1/prescriptions/history/?paciente_id=` | Histórico terapêutico |
| `GET/POST/PATCH` | `/api/v1/treatments/` | Tratamentos |
| `POST` | `/api/v1/treatments/{id}/finish/` | Concluir tratamento |
| `GET/POST` | `/api/v1/evolutions/` | Evolução clínica |
| `GET/POST` | `/api/v1/discharges/` | Alta médica |
| `GET/POST` | `/api/v1/followups/` | Seguimento (cria consulta futura) |

### Permissões RBAC (médico)

`doctors.prescription` · `doctors.treatment` · `doctors.evolution` · `doctors.discharge` · `doctors.followup`

### Rotas frontend — Médico

| Rota | Descrição |
|------|-----------|
| `/doctor` | Painel médico |
| `/doctor/prescriptions` | Prescrições |
| `/doctor/treatments` | Tratamentos |
| `/doctor/evolution` | Evolução clínica |
| `/doctor/history` | Histórico terapêutico |
| `/doctor/discharge` | Alta médica |

Documentação: `docs/Doctors/README.md`

### API — Notificações (Sprint 12)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET/POST/PATCH/DELETE` | `/api/v1/notifications/` | Centro de notificações |
| `POST` | `/api/v1/notifications/{id}/read/` | Marcar como lida |
| `POST` | `/api/v1/notifications/{id}/archive/` | Arquivar |
| `GET` | `/api/v1/notifications/unread/` | Não lidas + contador |
| `GET` | `/api/v1/notifications/history/` | Histórico |
| `POST` | `/api/v1/notifications/email/test/` | E-mail de teste |
| `GET` | `/api/v1/notifications/email/history/` | Histórico e-mail |
| `POST` | `/api/v1/notifications/sms/test/` | SMS de teste |
| `GET` | `/api/v1/notifications/sms/history/` | Histórico SMS |
| `CRUD` | `/api/v1/notifications/templates/email/` | Templates e-mail |
| `CRUD` | `/api/v1/notifications/templates/sms/` | Templates SMS |
| `GET/PATCH` | `/api/v1/notifications/preferences/` | Preferências |
| `GET` | `/api/v1/dashboard/notifications/` | KPIs |

### Permissões RBAC (notificações)

`notifications.view` · `notifications.create` · `notifications.edit` · `notifications.delete` · `notifications.send` · `notifications.template` · `notifications.settings` · `notifications.history`

### Rotas frontend — Notificações

| Rota | Descrição |
|------|-----------|
| `/notifications` | Centro de notificações |
| `/notifications/history` | Histórico de e-mails |
| `/notifications/templates` | Templates |
| `/notifications/preferences` | Preferências |

Documentação: `docs/Notifications/README.md`

## Perfis de utilizador (RBAC)

- `ADMINISTRADOR`
- `RECECIONISTA`
- `MEDICO`
- `ENFERMEIRO`
- `LABORATORIO`
- `FINANCEIRO`
- `DIRECTOR`

## Comandos úteis

```bash
# Parar serviços Docker
docker compose down

# Ver logs
docker compose logs -f

# Migrações
cd backend && python manage.py makemigrations && python manage.py migrate

# Semear permissões RBAC (patients.*, users.*, etc.)
cd backend && python manage.py seed_rbac

# Build de produção do frontend
cd frontend && npm run build

# Testes de lint do frontend
cd frontend && npm run lint
```

## Sprint atual

**Sprint 2** — Ambiente de desenvolvimento configurado (backend, frontend, Docker, autenticação base).

**Sprint 2.1** — Reorganização arquitetural (apps de domínio, `core/`, componentes UI, serviços e tipos modulares).

**Sprint 3** — Gestão de Utilizadores, RBAC, Auditoria, Dashboard Admin.

**Sprint 3.5** — Fundação empresarial: Redis, Celery, event bus, health probes, apps `settings`/`files`/`analytics`, design system e estrutura `features/` (sem alterar contratos existentes).

**Sprint 4** — Gestão de Pacientes: backend completo (CRUD, RBAC, auditoria, recursos aninhados), frontend em `features/patients/`, integração com dashboard, menu, Docker e health checks.

**Sprint 5** — Módulo de Receção: check-in, fila de espera, encaminhamentos, KPIs, integração com Pacientes, RBAC, auditoria, cache Redis e frontend em `features/reception/`.

**Sprint 7 Fase 1** — Módulo de Laboratório: recepção e gestão de pedidos das consultas, workflow completo, KPIs, RBAC, auditoria e frontend em `features/laboratory/`.

**Sprint 7 Fase 2** — Resultados Laboratoriais: modelos `ResultadoLaboratorial`, parâmetros, anexos, validação/publicação, integração PCE e dashboard, Celery preparado, frontend em `features/laboratory/results/`.

**Sprint 8 Fase 1** — Faturação: serviços, orçamentos, faturas, pagamentos, recibos, histórico financeiro, RBAC, auditoria, dashboard financeiro, frontend em `features/billing/`.

**Sprint 8 Fase 2** — Módulo Financeiro: caixa, movimentos, despesas, categorias, fluxo de caixa, relatórios, integração automática com Billing, RBAC, auditoria, cache Redis, Celery preparado, frontend em `features/finance/`. **112 testes** pytest verdes.

**Sprint 9** — Relatórios e Business Intelligence: relatórios clínicos/operacionais/financeiros, exportação PDF/Excel/CSV, dashboard executivo, séries temporais, cache Redis (120s), RBAC, auditoria, event bus, perfil `DIRECTOR`, frontend em `features/reports/`. **152 testes** pytest verdes.

**Sprint 10** — Administração e Configuração: dados da clínica, departamentos, especialidades, consultórios, horários, tipos de consulta, laboratório, faturação, segurança, e-mail, feature flags, backups, monitorização, dashboard do sistema, frontend em `features/settings/`. **184 testes** pytest verdes.

**Sprint 11** — Módulo Médico: prescrições, medicamentos, posologia, plano terapêutico, tratamentos, evolução clínica, alta médica, seguimento com criação automática de consulta, RBAC `doctors.*`, auditoria, event bus, cache Redis (TTL 120s), Celery preparado, frontend em `features/doctors/`. **201 testes** pytest verdes.

**Sprint 12** — Notificações e Comunicações: notificações internas, e-mail, SMS, templates, preferências, centro de notificações, fila, event bus integrado, dashboard `/dashboard/notifications/`, RBAC `notifications.*`, frontend em `features/notifications/`. **226 testes** pytest verdes.

**Sprint 13** — Otimização e Produção: performance (queries, cache central), segurança (rate limit, brute-force, headers), logging estruturado, health checks avançados, StorageService, exportações melhoradas, Celery retry, frontend (lazy, ErrorBoundary, breadcrumbs, tema). Ver `docs/Performance.md`, `docs/Security.md`, `docs/Production.md`, `docs/Monitoring.md`.

**Sprint 6 Fase 2** — Prontuário Clínico Eletrónico (PCE): sinais vitais, SOAP, diagnósticos CID-10, pedidos lab/imagiologia, seguimento, auditoria completa, UI com separadores e resumo do paciente.

**Sprint 6 Fase 1** — Consultas médicas: agenda, calendário, CRUD, confirmação, início/conclusão/cancelamento, validação de sobreposição de médicos, integração com receção (`assign-to-doctor` → `EM_ESPERA`), histórico clínico, KPIs (`/dashboard/consultas/`), RBAC completo, auditoria `CONSULTA_*`, Celery preparado e frontend em `features/appointments/` com rotas `/appointments/*` (rotas `/consultations/*` mantidas).

## Documentação

Consulte a pasta `docs/` para:

- **Arquitetura** — Estrutura e princípios do sistema
- **SRS** — Especificação de requisitos
- **API** — Documentação da API
- **Diagramas** — Arquitetura e fluxos
- **Manuais** — Manuais de utilizador e técnico
- **Reuniões** — Atas e notas

## Licença

Projeto proprietário — SauVida. Todos os direitos reservados.
