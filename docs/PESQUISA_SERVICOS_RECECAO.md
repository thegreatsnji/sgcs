# Pesquisa de serviços na Receção

## UI

`InvoiceCreatePage` + componente `ServiceSearchPicker`:

- Pesquisa por nome ou código
- Filtro por categoria
- Lista só serviços **activos** (`operacional=1` na API)
- Exibe departamento e preço (somente leitura)
- Quantidade, subtotal, remover linha antes de criar fatura

## API

`GET /api/v1/billing/services/?activo=true&operacional=1&search=hemo`

Exclui `INTERNAMENTO` e códigos em `EXCLUDED_SERVICE_CODES`.

## Permissões

Receção: `billing.view`, `billing.create` — **sem** alterar `preco` no catálogo.
