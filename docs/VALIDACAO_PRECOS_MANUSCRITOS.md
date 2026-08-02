# Validação de preços manuscritos

Ficheiro: `backend/data/validacao_precos_manuscritos.csv`

Todos os valores manuscritos estão marcados como **`ATUALIZACAO_MANUSCRITA_PENDENTE_VALIDACAO`**.

**Regra:** nenhum preço manuscrito substitui automaticamente o preçário impresso nem o Catálogo V1.

| Código | Situação |
|---|---|
| LAB-HEMO-MAN | Duplicado / manuscrito — unificar com hemograma |
| LAB-WIDALL | Nome ilegível — confirmar (provável Widal) |
| LAB-G-E | Abreviatura — confirmar (provável Gota Espessa) |
| LAB-GLICEMIA | Conflito impresso vs manuscrito |
| LAB-GLICOSE | Cruzar com Glicemia |

Preencher `decisao_clinica`, `preco_final_aprovado_fcfa`, `confirmado_por` e `data_confirmacao` antes de uma eventual `SAUVIDA_V1_1`.
