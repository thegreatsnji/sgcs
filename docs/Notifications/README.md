# Módulo de Notificações — SGCS

Sistema centralizado de notificações internas, e-mail, SMS, templates e preferências.

## Modelos

- `Notificacao` — notificações internas e fila
- `TemplateEmail` / `TemplateSMS` — templates com variáveis `{{nome}}`, `{{consulta}}`, etc.
- `PreferenciaNotificacao` — preferências por utilizador
- `HistoricoEmail` / `HistoricoSMS` — histórico de envios
- `FilaNotificacao` — fila de processamento

## Endpoints

| Método | URL | Descrição |
|--------|-----|-----------|
| CRUD | `/api/v1/notifications/` | Notificações |
| POST | `/api/v1/notifications/{id}/read/` | Marcar como lida |
| POST | `/api/v1/notifications/{id}/archive/` | Arquivar |
| GET | `/api/v1/notifications/unread/` | Não lidas + contador |
| GET | `/api/v1/notifications/history/` | Histórico do utilizador |
| POST | `/api/v1/notifications/email/test/` | E-mail de teste |
| GET | `/api/v1/notifications/email/history/` | Histórico e-mail |
| POST | `/api/v1/notifications/sms/test/` | SMS de teste |
| GET | `/api/v1/notifications/sms/history/` | Histórico SMS |
| CRUD | `/api/v1/notifications/templates/email/` | Templates e-mail |
| CRUD | `/api/v1/notifications/templates/sms/` | Templates SMS |
| GET/PATCH | `/api/v1/notifications/preferences/` | Preferências |
| GET | `/api/v1/dashboard/notifications/` | KPIs |

## Permissões

`notifications.view` · `notifications.create` · `notifications.edit` · `notifications.delete` · `notifications.send` · `notifications.template` · `notifications.settings` · `notifications.history`

## Event Bus

Subscrição automática a eventos de `patients.*`, `billing.*`, `laboratory.*`, `doctors.*`, `finance.*`, `reports.*`, `settings.*`, `authentication.*`.

## Celery

`notifications.enviar_email` · `notifications.enviar_sms` · `notifications.processar_fila` · `notifications.reenviar_falhas` · `notifications.limpar_notificacoes_antigas`

## Frontend

Rotas: `/notifications`, `/notifications/history`, `/notifications/templates`, `/notifications/preferences`

Componente `NotificationBell` no header com contador de não lidas.
