# Sprint 21 Fase 4 — Integridade dos pacientes importados

**Lote:** `SAUVIDA-HIST-V1`  
**N:** 156  
Sem identificadores pessoais.

| Verificação | Resultado |
| --- | ---: |
| Pacientes do batch | 156 |
| `migration_id` único e não vazio | 156 / 0 duplicados / 0 vazios |
| Nome (`first_name`) não vazio | 156 |
| `source=MIGRACAO_EXCEL_SAUVIDA` | 156 |
| `import_batch=SAUVIDA-HIST-V1` | 156 |
| `dados_verificados=false` | 156 |
| `dados_verificados=true` | 0 |
| Pacientes bloqueados importados | 0 |
| Duplicados técnicos | 0 |
| Merge automático | não |
| Telefone vazio (não inventado) | 150 |
| Data de nascimento vazia (não inventada) | 156 |
| Sexo vazio (não inventado) | 156 |
| Pacientes SGCS pré-existentes (id 1–10) alterados | 0 |

A data de criação coincide com a importação de 2026-08-17 (Fase 3). Actor `admin@sauvida.gw`.

Campos em falta **não** foram preenchidos com valores fictícios. Os utentes permanecem utilizáveis na Receção (telefone, residência, nascimento e sexo são editáveis sem apagar provenance).
