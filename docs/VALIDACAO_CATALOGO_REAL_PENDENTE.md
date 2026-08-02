# Validação do catálogo real — itens pendentes

- **12** linhas `REVISAR_COM_CLINICA` no CSV real.
- **21** linhas no ficheiro `catalogo_real_validacao_clinica.csv` (pendentes + códigos em conflito).
- Apply do import **não** executado até preenchimento de `preco_confirmado_fcfa` na ficha.

Processo: preencher CSV de validação → assinar ficha → actualizar catálogo → dry-run → apply.

Ver `docs/FICHA_VALIDACAO_CATALOGO_REAL.md` e `docs/IMPORTACAO_FINAL_CATALOGO_REAL.md`.
