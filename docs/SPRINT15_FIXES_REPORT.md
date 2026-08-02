# Relatório — Correções Sprint 15 (estabilização SauVida)

**Data:** 2026-07-31  
**Referência:** `docs/AUDITORIA_SPRINT15.md`

## 1. Permissões adicionadas à Receção (`RECECIONISTA`)

| Intenção operacional | Código RBAC no SGCS |
|----------------------|---------------------|
| Ver serviços / faturas / pagamentos (listagens) | `billing.view` |
| Criar fatura | `billing.create` |
| Alterar fatura (não paga) | `billing.edit` |
| Registar e confirmar pagamento | `billing.payment` |
| Listar / ver recibos | `billing.receipt` |
| Imprimir recibo | `billing.print` |
| Histórico financeiro do paciente | `billing.view` (API `patient-history`) |

Ficheiro: `backend/apps/users/management/commands/seed_rbac.py`

## 2. Permissões não concedidas / bloqueadas à Receção

- `billing.delete`, `billing.export`, `billing.quote` (orçamentos não obrigatórios no perfil receção)
- Todo o módulo `finance.*` (caixa, despesas, dashboard financeiro)
- `reports.*`, `settings.*`, `users.*`, auditoria, backups, feature flags

## 3. Menus alterados

`frontend/src/constants/navigation.ts` — perfil `RECECIONISTA`:

- Painel, Pacientes, **Marcações**, Fila, **Triagem** (`/reception/check-in`)
- **Faturação**, **Pagamentos**, **Recibos** (condicionados a `billing.view`)
- Sem Financeiro, Caixa, Administração, Monitorização, Backups

Textos: `frontend/src/constants/uiCopy.ts` (`appointmentsSchedule`, `payments`, `receipts`).

## 4. Rotas validadas

- `/billing/*` — `PermissionRoute` com `billing.view` / `billing.create`
- `/finance/*` — inacessível à Receção (sem `finance.view`)
- `/reception/check-in`, `/reception/queue` — receção existente
- API billing e `patient-history` — testes em `test_sprint15_reception_billing.py`

## 5. Fluxo de faturação validado

Paciente → serviço → fatura → pagamento (total/parcial) → confirmação → recibo → histórico — via **único** módulo `billing` (testes API receção).

## 6. Módulo `finance`

- **Não removido**; documentado em `docs/DECISAO_FATURACAO_RECECAO.md` como administrativo/legado.
- Receção sem menu nem permissões; Director mantém acesso.

## 7. Perfis extra

- `ENFERMEIRO`, `FINANCEIRO` mantidos no enum; ver `docs/PERFIS_NAO_UTILIZADOS.md`.
- `seed_demo` não cria estes perfis; `ASSIGNABLE_ROLES` já exclui-os na UI.
- Grupo RBAC «Financeiro» removido de `DEFAULT_GROUPS`.

## 8. Internamento

- `docs/ITENS_NAO_APLICAVEIS.md`
- `clinic_scope.py`, import CSV, listagem API, dados `data/clinic/*` actualizados.

## 9. Preparação catálogo

- `docs/READINESS_CATALOGO_SAUVIDA.md`

## 10. Ficheiros alterados

| Ficheiro | Alteração |
|----------|-----------|
| `backend/apps/users/management/commands/seed_rbac.py` | RBAC receção + grupos |
| `backend/apps/billing/clinic_scope.py` | **novo** |
| `backend/apps/billing/views.py` | Exclusão INTERNAMENTO na listagem |
| `backend/apps/billing/management/commands/import_servico_catalog.py` | Skip categorias excluídas |
| `backend/apps/billing/tests/test_billing.py` | RBAC receção positivo |
| `backend/apps/billing/tests/test_sprint15_reception_billing.py` | **novo** |
| `frontend/src/constants/navigation.ts` | Menu receção |
| `frontend/src/constants/uiCopy.ts` | PT labels |
| `data/clinic/catalogo_servicos_sauvida.csv` | INT inactivo |
| `data/clinic/departamentos_sauvida.json` | Dept INT inactivo |
| `docs/DECISAO_FATURACAO_RECECAO.md` | **novo** |
| `docs/PERFIS_NAO_UTILIZADOS.md` | **novo** |
| `docs/ITENS_NAO_APLICAVEIS.md` | **novo** |
| `docs/READINESS_CATALOGO_SAUVIDA.md` | **novo** |

## 11. Migrations

Nenhuma migration criada (`makemigrations --check` OK).

## 12. Testes

- Novos: `test_sprint15_reception_billing.py` (RBAC, seed_demo, internamento, director reports).
- Billing: 23 testes focados — **passaram**.
- Suite completa: **262 passed**, 1 aviso de teardown de BD em teste Celery (`test_sprint13`); **exit 0** (~7 min).

## 13. Build

`npm run build` — **sucesso** (tsc + vite).

## 14. Lint

`npm run lint` — **0 erros**, 7 avisos pré-existentes (react-refresh / hooks).

## 15. Riscos restantes

- Duplicação conceptual billing vs finance se Director usar caixa em paralelo à receção.
- Orçamentos (`billing.quote`) não atribuídos à receção — fluxo directo fatura ainda suportado.
- Departamento não ligado ao modelo `Servico` (ver readiness catálogo).

## 16. Recomendação próxima etapa

1. `python manage.py seed_rbac` em todos os ambientes.
2. Importar preçário real com `import_servico_catalog` após validação `--dry-run`.
3. Formação receção no fluxo `/billing` (faturas, pagamentos, recibos, histórico).
4. Decidir se orçamentos entram no perfil receção (`billing.quote`).
