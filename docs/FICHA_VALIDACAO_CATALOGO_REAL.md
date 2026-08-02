# Ficha de validação — catálogo real (OCR)

**Clínica:** SauVida — Guiné-Bissau  
**Origem:** 7 fotografias (`OCR_FOTOGRAFIAS_CLINICA`)  
**Ficheiro de trabalho:** `backend/data/catalogo_real_validacao_clinica.csv`  
**Catálogo original:** `backend/data/catalogo_servicos_sauvida_real.csv` (não alterado por este processo)

---

## Laboratório — pendências

| Código | Nome | Preço extraído (FCFA) | Tipo pendência | Decisão clínica | Confirmado por | Data | Observações |
|---|---|---:|---|---|---|---|---|
| LAB-LINHA-SEM-NOME | [linha sem nome] | 4 000 | PREÇO_ILEGÍVEL / NOME_INCOMPLETO | | | | |
| LAB-VIH-AG-AC-4A-GERACAO | VIH (AG/AC) 4a Geração | 8 000 | PREÇOS_DIVERGENTES | | | | vs 4 500 noutra folha |
| LAB-PROGESTERONA | Progesterona | — | PREÇO_AUSENTE | | | | |
| LAB-RUBEOLA-IGG-IGM | Rubéola IGG IGM | — | PREÇO_AUSENTE | | | | |
| LAB-FACTOR-REUMATOIDE | Factor Reumatoide | 4 000 | PREÇOS_DIVERGENTES | | | | vs 8 000 noutra foto |
| LAB-TESTE-DE-GRAVIDEZ | Teste De Gravidez | 2 500 | PREÇOS_DIVERGENTES | | | | vs 2 000 / 4 000 |
| LAB-MIOGLOBINA | Mioglobina | — | PREÇO_AUSENTE | | | | |
| LAB-G-E | G.E. | 2 000 | CLASSIFICAÇÃO_DUVIDOSA | | | | Confirmar exame |
| LAB-HEMO-MAN | Hemograma completo | 4 000 | POSSÍVEL_DUPLICADO | | | | vs LAB-HEMO |
| LAB-WIDALL | Widall | 4 000 | CLASSIFICAÇÃO_DUVIDOSA | | | | Provável Widal |
| LAB-GLICEMIA | Glicemia | 2 000 | PREÇOS_DIVERGENTES | | | | vs 4 000 Bioquímica |

## Cartões / outros

| Código | Nome | Preço extraído | Tipo pendência | Decisão | Confirmado por | Data |
|---|---|---:|---|---|---|---|
| CARD-CARTAO-DE-TETANO | CARTÃO DE TETANO | — | PREÇO_AUSENTE | | | |

## Conflitos (códigos confirmados no CSV mas em grupo de duplicado)

| Código | Nome | Preço extraído | Tipo | Decisão | Confirmado por | Data |
|---|---|---:|---|---|---|---|
| LAB-HCG | Teste de gravidez | 2 000 | PREÇOS_DIVERGENTES | | | |
| LAB-HEMO | Hemograma Completo | 4 000 | POSSÍVEL_DUPLICADO | | | |
| LAB-TSH | TSH | 6 000 | POSSÍVEL_DUPLICADO | | | |
| LAB-TOXOPLASMOSE | Toxoplasmose | 8 000 | POSSÍVEL_DUPLICADO | | | |

---

**Responsável clínico / administrativo**

Nome: _________________________________  

Função: _________________________________  

Data: _________________________________  

Assinatura: _________________________________
