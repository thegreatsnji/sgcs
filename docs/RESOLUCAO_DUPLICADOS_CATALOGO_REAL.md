# Resolução de duplicados — catálogo real SauVida

Fonte: `backend/data/catalogo_real_duplicados.json` (6 grupos). **Nenhuma linha foi eliminada automaticamente.**

| Grupo | Itens | Preços | Situação | Decisão necessária | Estado |
|---|---|---:|---|---|---|
| 1 — Teste de gravidez | LAB-HCG, LAB-TESTE-DE-GRAVIDEZ (×2) | 2 000 / 2 500 FCFA | MESMO_SERVIÇO_COM_PREÇOS_DIFERENTES | Confirmar preço único e código canónico | NECESSITA_VALIDACAO |
| 2 — Hemograma Completo | LAB-HEMO, LAB-HEMO-MAN | 4 000 / 4 000 FCFA | MESMO_SERVIÇO (possível duplicado OCR) | Unificar ou desactivar duplicado | NECESSITA_VALIDACAO |
| 3 — VIH (AG/AC) 4ª geração | LAB-VIH-AG-AC-4A-GERACAO (×2) | 4 500 / 8 000 FCFA | PREÇOS_DIVERGENTES entre folhas | Confirmar preço oficial | NECESSITA_VALIDACAO |
| 4 — TSH | LAB-TSH (×2 no CSV) | 6 000 FCFA | POSSÍVEL_DUPLICADO (mesmo código) | Confirmar se é uma única entrada | NECESSITA_VALIDACAO |
| 5 — Toxoplasmose | LAB-TOXOPLASMOSE (×2) | 8 000 FCFA | POSSÍVEL_DUPLICADO | Confirmar duplicado de importação | NECESSITA_VALIDACAO |
| 6 — Progesterona | LAB-PROGESTERONA (×2) | ausente / pendente | NOME_INCOMPLETO + duplicado | Confirmar preço e linha única | NECESSITA_VALIDACAO |

## Regras até decisão clínica

- Itens em `REVISAR_COM_CLINICA` permanecem pendentes no CSV de validação.
- O import **não** escolhe o preço mais alto nem o mais baixo em conflito.
- Preços conflitantes **não** são promovidos a confirmados sem assinatura na ficha de validação.
