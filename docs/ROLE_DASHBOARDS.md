# Painéis por perfil — SGCS SauVida

## Rotas

| Perfil | Rota | Página |
|--------|------|--------|
| Administrador | `/dashboard/admin` | `AdminRoleDashboardPage` |
| Director | `/dashboard/director` | `DirectorRoleDashboardPage` |
| Médico | `/dashboard/medico` | `DoctorRoleDashboardPage` |
| Receção | `/dashboard/rececao` | `ReceptionRoleDashboardPage` |
| Laboratório | `/dashboard/laboratorio` | `LaboratoryRoleDashboardPage` |

Redireccionamento pós-login: `frontend/src/utils/roleRouting.ts`.

Menus: `frontend/src/constants/navigation.ts` (filtrados por permissões RBAC).

## Conteúdo esperado

### Administrador

Estado do sistema, utilizadores, sessões, PostgreSQL/Redis/Celery, backups, segurança, auditoria, atalhos administrativos.

### Director

Receita do dia/mês, despesas, lucro, pacientes, consultas, laboratório, pagamentos pendentes, desempenho médico, serviços mais vendidos, tendências. **Sem** utilizadores, backups, feature flags nem monitorização de sistema.

### Médico

Consultas de hoje, pacientes em espera, seguimentos, resultados laboratoriais recentes, alertas clínicos, atalho para iniciar consulta, pesquisa de pacientes. **Sem** faturação/financeiro.

### Receção

Fila actual, consultas do dia, registos de entrada, novos pacientes, próximas consultas, acções rápidas. **Sem** prontuário clínico completo nem relatórios financeiros.

### Laboratório

Pedidos pendentes, fila de colheitas, em processamento, resultados por validar, concluídos hoje, urgências, tempo médio. **Sem** faturação, financeiro e configurações.

## FINANCEIRO

Perfil técnico no RBAC sem utilizadores associados. O Director assume as responsabilidades financeiras na UI.
