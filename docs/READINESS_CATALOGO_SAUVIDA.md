# Prontidão — catálogo de serviços SauVida

**Objectivo:** preparar importação do preçário real (próxima etapa), sem importar todos os preços agora.

## Modelo central

**`apps.billing.models.Servico`**

| Campo | Existe | Notas |
|-------|--------|-------|
| `codigo` | Sim | `unique=True`, max 30 |
| `nome` | Sim | max 150 |
| `descricao` | Sim | opcional |
| `categoria` | Sim | `CONSULTA`, `EXAME`, `PROCEDIMENTO`, `INTERNAMENTO`, `OUTRO` |
| `preco` | Sim | `Decimal`, FCFA (sem campo moeda separado — moeda na clínica via `PerfilClinica.moeda`) |
| `activo` | Sim | boolean |
| `created_at` / `updated_at` | Sim | `TimestampMixin` |

### Relações

| Relação pedida | Estado |
|----------------|--------|
| Departamento | **Ausente** no modelo `Servico` — departamentos em `settings.Departamento`; ligação indirecta apenas via documentação/roadmap |
| Categoria | Sim — campo `categoria` (choices) |
| Faturação | Sim — `ItemFatura`, `ItemOrcamento` FK para `Servico` |
| Laboratório | Indirecta — exames lab como `Servico` categoria `EXAME` + `ExameLaboratorial` |
| Código único | Sim — constraint `unique` em `codigo` |
| Prevenção duplicados | Sim — `update_or_create(codigo=...)` no import; API valida unicidade |

## Migração necessária?

**Não** para importação inicial do CSV actual.  
Futuro opcional: FK `departamento` em `Servico` se a direcção exigir relatórios por departamento.

## Endpoints existentes

- `GET/POST /api/v1/billing/services/`
- `GET/PATCH/DELETE` serviço por id (delete lógico → `activo=False`)
- Filtros: `categoria`, `activo`, `search`
- Comando: `python manage.py import_servico_catalog [--file] [--dry-run]`

## Frontend existente

- `ServicesListPage`, `ServiceFormPage`, selecção de serviços em `InvoiceCreatePage` / `QuoteCreatePage` (filtro `activo: true`).

## Testes existentes

- `apps/billing/tests/test_billing.py`
- `apps/billing/tests/test_sprint15_reception_billing.py` (exclusão `INTERNAMENTO`)

## Alterações mínimas já aplicadas (Sprint 15 fixes)

1. `clinic_scope.EXCLUDED_SERVICE_CATEGORIES` + exclusão no import e listagem API.
2. CSV/departamentos SauVida alinhados (`INT` inactivo).

## Lacunas para o próximo prompt

1. Valores reais no CSV (substituir placeholders).
2. Opcional: campo `departamento_id` ou tabela de ligação serviço↔departamento.
3. Regras de IVA/desconto globais em `settings` (já existe config billing em settings API).
4. Validação de preço mínimo/máximo por categoria (não implementada).

## Comando sugerido (quando preços confirmados)

```bash
python manage.py seed_rbac
python manage.py import_servico_catalog --file data/clinic/catalogo_servicos_sauvida.csv --dry-run
python manage.py import_servico_catalog --file data/clinic/catalogo_servicos_sauvida.csv
```
