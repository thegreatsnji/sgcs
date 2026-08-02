# Sprint 18 — Importação catálogo real (OCR)

## Resumo

- **133** serviços extraídos das fotografias.
- **121** com `preco_confirmado=TRUE`.
- **12** pendentes / `REVISAR_COM_CLINICA`.
- **98** laboratório; **4** consultas; restantes ecografia, cirurgia, maternidade, farmácia urgência, material, cartões, observação.

## Dry-run

```
Criados: 121 | Pendentes revisão: 12
```

(Com `--materialize-without-price` — serviços confirmados criados; pendentes materializados sem preço.)

## Apply

**Não executado automaticamente** nesta entrega — requer aprovação após revisão clínica dos 12 itens e conflitos em `catalogo_real_duplicados.json`.

## Testes

- `apps/billing/tests/test_catalogo_real_ocr.py`
- Regeneração: `scripts/build_catalogo_real_from_ocr.py`

## Próximo passo

1. Clínica valida conflitos (gravidez, factor reumatoide, Glicemia, etc.).
2. Ajustar CSV se necessário (sem inventar — só corrigir com confirmação).
3. `--apply` + alinhamento laboratorial.
