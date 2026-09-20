# Auditoria RBAC visual e funcional — SauVida SGCS

## Problema UAT

No perfil RECECIONISTA a sidebar mostrava **«Exames lab.»** e `/reception/lab-orders` apresentava **duas** sub-navs (Receção + Faturação), sugerindo trabalho clínico de laboratório.

## Decisão

| Item | Classificação | Acção |
|------|---------------|--------|
| Painel | ESSENCIAL | Mantido na sidebar |
| Atendimento rápido | ESSENCIAL | Mantido na sidebar |
| Fila de atendimento | ESSENCIAL | Mantido sidebar + ReceptionSubNav |
| Faturação | ESSENCIAL | Mantido na sidebar |
| Pacientes | ESSENCIAL | Mantido |
| Marcações | ESSENCIAL | Mantido |
| Exames lab. (sidebar) | INDEVIDA | **Removido** da sidebar principal |
| Exames a regularizar | ESSENCIAL (financeiro) | Em **BillingSubNav** |
| Triagem isolada (`/check-in`) | SECUNDÁRIA | **Redirect** → `/reception/atendimento?passo=1` |
| Encaminhamentos | LEGADO | **Removido** da ReceptionSubNav (médico no Atendimento + Fila) |
| Serviços (catálogo) | READ-ONLY balcão | Visível; criar/editar só `billing.delete` |
| Orçamentos | SECUNDÁRIA / não piloto | Só com `billing.quote` (Receção não tem) |
| Reduções | OPERACIONAL | Mantido na BillingSubNav (Receção: Faturas · Serviços · Exames · Reduções) |
| Lab clínico `/laboratory` | INDEVIDA | Sem permissão; sem link UI |
| Stock | INDEVIDA | Sem permissão; sem link UI |

## Matriz de visibilidade UI

| Área | Receção | Enfermeiro | Médico | Lab | Director | Admin |
|------|---------|------------|--------|-----|----------|-------|
| Painel | VISÍVEL | VISÍVEL | VISÍVEL | VISÍVEL | VISÍVEL | VISÍVEL |
| Atendimento rápido | OPERACIONAL | OCULTO | OCULTO | OCULTO | OCULTO | VISÍVEL* |
| Fila | OPERACIONAL | OCULTO | OCULTO | OCULTO | OCULTO | VISÍVEL* |
| Faturação | OPERACIONAL | OCULTO | OCULTO | OCULTO | READ-ONLY | VISÍVEL |
| Pacientes | OPERACIONAL | OPERACIONAL | OPERACIONAL | OCULTO | READ-ONLY | VISÍVEL |
| Marcações | OPERACIONAL | OCULTO | OPERACIONAL | OCULTO | READ-ONLY | VISÍVEL |
| Lab clínico | OCULTO | OCULTO | READ-ONLY† | OPERACIONAL | READ-ONLY | VISÍVEL |
| Exames a regularizar | OPERACIONAL‡ | OCULTO | OCULTO | OCULTO | OCULTO | VISÍVEL* |
| Stock | OCULTO | OPERACIONAL | READ-ONLY | OCULTO | READ-ONLY | VISÍVEL |
| Consulta clínica | OCULTO | OCULTO | OPERACIONAL | OCULTO | OCULTO | VISÍVEL |
| Relatórios | OCULTO | OCULTO | OCULTO | OCULTO | OPERACIONAL | VISÍVEL |
| Administração | OCULTO | OCULTO | OCULTO | OCULTO | OCULTO | OPERACIONAL |

\* via rotas admin / permissões amplas  
† resultados lab (`laboratory.results.view`)  
‡ dentro de Faturação (`/reception/lab-orders`), não lab clínico  

## Protecção

- **Frontend:** `buildSidebarConfig`, `BillingSubNav`, `ReceptionSubNav`, `PermissionRoute` / `RoleGuard`; AppShell usa o mesmo sidebar no drawer mobile.
- **Backend:** permissões seed inalteradas para o perímetro clínico; catálogo de serviços write passou a `billing.delete` (Receção: list/retrieve apenas).
- Bridge: `GET/POST pending-clinical-lab-orders` / `mark_lab_order_billed` continua com `reception.view` + `billing.edit` (AND).

## Copy

«Exames lab.» → **«Exames a regularizar»** (`UI_COPY.nav.labOrdersToSettle`).
