# Catálogo SauVida V1 (congelado)

**Versão:** `SAUVIDA_V1`  
**Data:** 2026-07-31  
**Origem:** OCR de 7 fotografias (`OCR_FOTOGRAFIAS_CLINICA`)  
**Estado:** CONGELADO — não editar ficheiros em `backend/data/releases/`

## Ficheiros imutáveis

| Ficheiro | Registos | SHA-256 |
|---|---:|---|
| `catalogo_sauvida_v1.csv` | 119 serviços | `32cc9123087de039c0bef965aa61cdee4cd63d50295a32278711fe698000104f` |
| `exames_laboratoriais_sauvida_v1.csv` | 87 exames | `c5e35bd97b3352705f9a1132094691ec51a4dcb3f08f94d0ee08d0a3bbeb6678` |
| `catalogo_sauvida_v1_manifest.json` | metadados | — |

## Contagens OCR vs V1

| Métrica | OCR real | V1 operacional |
|---|---:|---:|
| Serviços identificados | 133 | 119 (códigos únicos confirmados) |
| Preços confirmados (OCR) | 121 | 119 |
| Pendentes `REVISAR_COM_CLINICA` | 12 | 0 (excluídos do V1) |
| Exames laboratoriais | 97 | 87 (sem pendentes) |

A diferença 121→119 deve-se a **códigos duplicados** no CSV OCR (ex.: `LAB-TSH`, `LAB-TOXOPLASMOSE` repetidos); o congelamento mantém **uma linha confirmada por código**.

## Pendências fora do V1

Documentadas em `catalogo_real_validacao_clinica.csv` e `validacao_precos_manuscritos.csv`.

## Conflitos

6 grupos em `catalogo_real_duplicados.json` — decisão em `docs/DECISOES_CATALOGO_SAUVIDA_V1.md` (estado **PENDENTE_CLINICA** até assinatura).

## Regras de alteração

1. Não modificar `releases/*` após congelamento.  
2. Nova versão: `SAUVIDA_V1_1`, `SAUVIDA_V2`, etc.  
3. Regenerar com `python backend/scripts/freeze_catalogo_sauvida_v1.py` apenas após decisão clínica documentada.

## Validação

| Campo | Valor |
|---|---|
| Confirmado por | _(preencher na clínica)_ |
| Data confirmação | _(preencher)_ |
