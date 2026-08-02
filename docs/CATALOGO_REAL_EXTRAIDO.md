# Catálogo real extraído das fotografias

Fonte única: fotografias oficiais da clínica (julho 2026).  
Gerado por: `python backend/scripts/build_catalogo_real_from_ocr.py`

## Ficheiros

| Ficheiro | Descrição |
|----------|-----------|
| `backend/data/catalogo_servicos_sauvida_real.csv` | Serviços para faturação |
| `backend/data/exames_laboratoriais_reais.csv` | Tipos de exame ↔ serviço |
| `backend/data/catalogo_real_duplicados.json` | Sugestões de duplicados/conflitos |

## Regras aplicadas

- Ortografia mantida como no documento (`Bilirrulina`, `Jadel`, `Geneco-Obstetricia`, etc.).
- `preco_confirmado=TRUE` apenas com preço claramente visível e sem conflito documentado.
- Conflitos entre folhas → `estado=REVISAR_COM_CLINICA`, `preco_confirmado=FALSE`.
- Itens ilegíveis ou cortados **não** foram incluídos com preço inventado.

## Duplicados / conflitos (não eliminados)

Ver `catalogo_real_duplicados.json` e observações no CSV. Exemplos:

- Teste de gravidez — vários preços em folhas diferentes.
- Factor Reumatoide — 4.000 vs 8.000 cfa.
- Glicemia — manuscrito 2.000 vs Bioquímica 4.000.
- VIH 4ª geração — 4.500 vs 8.000 em folhas distintas.

## Regenerar

```bash
cd backend
python scripts/build_catalogo_real_from_ocr.py
```
