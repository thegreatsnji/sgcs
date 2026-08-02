# Sprint 18 — UAT por perfil

| Perfil | Capacidade | Estado | Evidência |
|---|---|---|---|
| ADMINISTRADOR | Catálogo, preço, import CLI, médicos, auditoria | APROVADO | RBAC + `test_sprint16/17/18` |
| DIRECTOR | Ver catálogo, histórico, relatórios; não alterar preço | APROVADO | `test_sprint17.TestPermissoesPreco` |
| RECECIONISTA | Faturar confirmados, pagamentos, recibos | APROVADO | `test_sprint15_reception_billing` |
| MEDICO | Consulta, pedidos lab; sem preço/pagamento | APROVADO | RBAC `doctors.*` / `billing.view` |
| LABORATORIO | Exames/resultados; sem preço/pagamento | APROVADO | RBAC laboratório |

Sessão presencial: repetir com contas demo documentadas em `docs/DEMO_DATA.md`.
