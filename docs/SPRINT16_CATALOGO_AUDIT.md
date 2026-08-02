# Sprint 16 — Auditoria técnica do catálogo (pré-implementação)

**Data:** 2026-07-31

| Componente | Estado actual | Lacuna | Alteração necessária | Risco |
|---|---|---|---|---|
| `billing.Servico` | Código, nome, categoria, preço, activo | Sem departamento, flags operacionais, moeda, auditoria de preço | Extender modelo + histórico `ServicoPrecoHistorico` | Migração; manter API retrocompatível |
| Categorias | 5 valores (`CONSULTA`, `EXAME`, …) | Categorias SauVida (Ecografia, Enfermagem, …) | Expandir `SERVICE_CATEGORIES` + aliases import | Dados legados `EXAME` mantidos |
| `settings.Departamento` | código, nome, activo | Sem ordem, responsável, localização | Campos opcionais Sprint 16 | Baixo |
| `settings.EspecialidadeMedica` | código, nome, activo | Sem duração, departamento | FK departamento + duração | Baixo |
| `settings.TipoExameLaboratorio` | código, categoria texto | Sem FK `Servico` | `servico` FK + metadados colheita | Sincronizar preço com Serviço |
| `ItemFatura` / `ItemOrcamento` | `preco`/`preco_unitario` snapshot | — | Nenhuma (já preserva histórico) | — |
| Laboratório `ExameLaboratorial` | Nome livre no pedido | Catálogo central | Ligar via `TipoExameLaboratorio.servico` | Médio |
| Consultas | `TipoConsulta.preco_base` | Duplica preço | Documentar: preço oficial = `Servico` | Confusão operacional |
| API `/billing/services/` | CRUD + search + activo | Filtros dept/esp; modo faturação | Filtros + `operacional=true` | Baixo |
| Permissions | `billing.view/create/edit` | Médico sem ver catálogo | `billing.view` para `MEDICO` | RBAC |
| Frontend serviços | Lista/form básicos | Pesquisa receção, filtros admin | `ServiceSearchPicker`, filtros | UX |
| Import | `import_servico_catalog` | Formato antigo, sem dept | `import_catalogo_sauvida` | Duplicar comandos — documentar depreciação |
| Seeds | `data/clinic/*.csv` com preços placeholder | Preços não confirmados | `backend/data/*` com `REVISAR_COM_CLINICA` | Não importar preços inventados |
| Médicos | `User` sem perfil clínico | Config agenda/serviço | `MedicoPerfil` 1:1 | Novo modelo pequeno |
| `PerfilClinica` | Campos base | contacto urgência, texto legal | Campos opcionais | Baixo |
| Auditoria preços | `AuditLog` genérico | Acção dedicada | `SERVICO_PRECO_ALTERADO` + histórico | Baixo |
| Internamento / farmácia | Categoria legada | Não aplicável SauVida | Exclusão import/UI (`clinic_scope`) | Baixo |

**Decisão:** reutilizar `Servico` como fonte única de preço; não duplicar modelos de catálogo.
