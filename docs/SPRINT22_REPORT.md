# Sprint 22 — Stock de urgência

**Estado:** `STOCK_URGENCIA_IMPLEMENTADO`

Gates: `manage.py check` OK · `makemigrations --check` OK · pytest **396 passed**, 2 skipped, **2 failed** pré-existentes na Receção · `npm run build` OK · lint sem erros novos.

Reutilizado `MedicamentoUrgencia` + `MovimentoStockUrgencia`. Sem farmácia comercial, fornecedores, POS ou compras.

## Entrega

- Modelo: campos categoria, validade, preço de referência, texto original de quantidade; movimentos com origem, utente, consulta; `PERDA_EXPIRACAO`.
- Endpoints `/api/v1/stock/` (e legado pharmacy).
- Perfil `ENFERMEIRO` já existia; permissões `stock.*`.
- UI `/stock` e `/stock/historico`.
- Importação `--dry-run` / `--apply` sem inventar quantidades.
- Stock negativo bloqueado; quantidade não editável; movimentos imutáveis.

## Pendências

- Quantidades físicas reais: a enfermeira confirma na ficha / na UI.
- Preços de referência: Direcção (Fase 6).
- Itens iniciais: 0 importados automaticamente nesta sprint (sem `manter_no_stock=SIM` + quantidade numérica na ficha).
