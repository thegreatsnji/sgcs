# Autorização de reduções

## Modelo

`ReducaoValorAutorizacao` — estados: `PENDENTE`, `APROVADA`, `REJEITADA`, etc.

## API

- `POST /api/v1/billing/reducoes/` — solicitar (rececionista).
- `POST /api/v1/billing/reducoes/{id}/aprovar/` — Director/Administrador.
- `POST /api/v1/billing/reducoes/{id}/rejeitar/` — Director/Administrador.
- `GET /api/v1/billing/reducoes/?estado=PENDENTE` — fila de pendentes.

## UI

`/billing/reducoes/pendentes` — página **Reduções pendentes**.

## Regras

- Rececionista não altera preço oficial do serviço.
- Não pode decidir a própria solicitação.
- Acima do limite: fatura bloqueada sem autorização aprovada.
