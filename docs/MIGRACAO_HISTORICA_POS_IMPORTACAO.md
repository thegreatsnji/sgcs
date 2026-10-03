# Validação pós-importação (quando o apply for autorizado)

Ainda **não** houve apply. Use esta lista depois das duas etapas.

## Após `--patients-only`

- Total criado = pacientes prontos do dry-run (hoje 156, se as decisões de duplicados não mudarem).
- `migration_id` únicos em `Patient.metadata`.
- Nenhum dos 38 utentes bloqueados por duplicado.
- Telefone/sexo/nascimento só existem quando estavam na fonte.
- `verification_state=IMPORTADO_NAO_VERIFICADO` e `dados_verificados=false`.
- `source=MIGRACAO_EXCEL_SAUVIDA` e `import_batch` correcto.

## Após `--history-only`

- Eventos por tipo próximos do dry-run (consultas, controlos, lab estruturado/textual, eco, cirurgia).
- Cada evento com paciente correcto, descrição original, médico original, valores no metadata.
- Sem SOAP, sinais vitais, resultados laboratoriais, notas operatórias, prescrições, faturas ou pagamentos.
- Datas suspeitas não importadas como válidas.
- Eventos sem paciente continuam só no CSV de arquivo.
- `record_class=HISTORICO_IMPORTADO` — não entra no caixa nem em recibos.

## Rollback de verificação

```bash
python manage.py rollback_sauvida_history --batch-id SAUVIDA-HIST-V1 --dry-run
```

Só remove objectos daquele lote. Utentes criados pela operação normal do SGCS permanecem.
