# Sprint 16 — Catálogo de serviços SauVida

## Modelo central

`billing.Servico` é a **fonte oficial de preço** (FCFA, campo `moeda` predefinido `FCFA`).

Relações: `departamento` → `clinic_settings.Departamento`, `especialidade` → `EspecialidadeMedica` (opcional).

Snapshots em `ItemFatura.preco` / `ItemOrcamento.preco_unitario` preservam histórico.

## Histórico de preços

`ServicoPrecoHistorico` + `AuditAction.SERVICO_PRECO_ALTERADO`. Apenas **ADMINISTRADOR** altera `preco` via API.

## Categorias

Ver `billing.constants.SERVICE_CATEGORIES` (13 operacionais + legado `EXAME`, `OUTRO`, `INTERNAMENTO`).

## API

- `GET /api/v1/billing/services/?search=&categoria=&departamento=&operacional=1`
- `GET /api/v1/billing/services/{id}/price-history/` (admin/director)

## Comando

`python manage.py import_catalogo_sauvida --dry-run` (predefinição)  
`python manage.py import_catalogo_sauvida --apply --update-existing`

Ficheiros: `backend/data/catalogo_servicos_sauvida.csv`, `departamentos_sauvida.json`, `especialidades_sauvida.csv`, `exames_laboratoriais_sauvida.csv`.
