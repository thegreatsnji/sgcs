# Relatório de reduções

**Endpoint:** `GET /api/v1/billing/reports/reducoes/`

**Filtros (query):** `de`, `ate`, `motivo`, `rececionista` (expansível).

**Indicadores:** número de reduções, totais oficial/cobrado/reduzido, média percentual, pendentes e rejeitadas (autorizações).

Dados derivados de `ItemFatura` com `valor_reducao > 0`.
