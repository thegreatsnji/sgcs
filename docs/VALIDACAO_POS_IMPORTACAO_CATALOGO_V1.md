# Validação pós-importação — Catálogo V1

Ambiente: `sgcs` @ `localhost`

| Verificação | Esperado | Obtido | Estado |
|---|---:|---:|---|
| Serviços SAUVIDA_V1 | 119 | 119 | APROVADO |
| Operacionais (activo, preço confirmado, não arquivado) | 119 | 119 | APROVADO |
| Activos | 119 | 119 | APROVADO |
| Preço confirmado | 119 | 119 | APROVADO |
| Arquivados V1 | 0 | 0 | APROVADO |
| Sem preço confirmado | 0 | 0 | APROVADO |
| Preços negativos | 0 | 0 | APROVADO |
| Códigos duplicados (global) | 0 | 0 | APROVADO |
| Eventos CATALOGO_REAL_IMPORTADO | >0 | 119 | APROVADO |
| Itens fatura (preservação) | — | 1 linhas | APROVADO |

## Por categoria

- CARTAO: 2
- CIRURGIA: 5
- CONSULTA: 4
- ECOGRAFIA: 3
- LABORATORIO: 85
- MATERIAL_CLINICO: 7
- MATERNIDADE: 1
- MED_URGENCIA: 9
- OBSERVACAO_CLINICA: 1
- PROCEDIMENTO: 2

Checksum catálogo (release): `32cc9123087de039c0bef965aa61cdee4cd63d50295a32278711fe698000104f`  
Actor importação: `admin@sauvida.ao` (eventos `CATALOGO_REAL_IMPORTADO`).

Apply 2026-08-02: 0 criados, 119 actualizados (BD já continha os códigos V1).

Nota: alterações em `Servico` não recalculam `ItemFatura` nem recibos já emitidos (snapshots por linha).