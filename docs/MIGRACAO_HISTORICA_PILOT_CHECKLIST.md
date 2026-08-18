# Checklist — piloto da migração histórica SauVida

Marcar SIM / NÃO / N/A. Sem passwords. Sem PII neste documento.

**Lotes:** `SAUVIDA-HIST-V1` (inicial) e, depois da validação clínica, `SAUVIDA-HIST-V1-REVIEW`.  
**Não** reaplicar o lote inicial para desbloquear registos.

## Infraestrutura

| Item | Critério | SIM | Data | Notas |
| --- | --- | --- | --- | --- |
| PostgreSQL | 16+ acessível; BD alvo correcta (não produção clínica sem autorização) | | | |
| Docker Compose | `sgcs-db`, `sgcs-backend`, frontend no mesmo ambiente | | | |
| Disco | Espaço para dump SQL + logs + Excel privado | | | |
| HTTPS | Certificado válido no piloto (se exposto na rede) | | | |
| Utilizadores | Contas reais por perfil; actor Administrador existente | | | |
| Permissões ficheiros | `backend/data/private/sauvida_migration/` só equipa de migração | | | |

## Código e catálogo

| Item | Critério | SIM | Data | Notas |
| --- | --- | --- | --- | --- |
| Checkout / tag | Commit/tag documentado (`git log -1`) | | | |
| Migrations | `makemigrations --check` + `migrate` aplicados | | | |
| `manage.py check` | 0 problemas | | | |
| Catálogo SauVida V1 | Serviços/exames operacionais alinhados | | | |
| Laboratório | Pedidos/resultados modernos **não** inventados pela migração | | | |
| Receção | Filas/atendimento operacionais (falhas pytest pré-existentes fora de âmbito) | | | |
| PatientHistory | Modelo com metadata de proveniência | | | |
| Auditoria | AuditLog activo; rollback **não** apaga trilha | | | |
| Logs | Pasta `docs/logs/` sem PII | | | |

## Dados privados

| Item | Critério | SIM | Data | Notas |
| --- | --- | --- | --- | --- |
| Excel original | SHA256 = `bfd987eec4a82c454d1a4519d460ef64fcad16b91dcb47af95fe6a6847ce6822` | | | |
| Staging CSVs | Presentes e gitignored | | | |
| Pacote validação | 6 Excel em `validation_pack/` preenchíveis | | | |
| Stock | 55 candidatos **não** importados | | | |

## Backup

| Item | Critério | SIM | Data | Notas |
| --- | --- | --- | --- | --- |
| Dump PostgreSQL | Tamanho > 0, cabeçalho `PostgreSQL database dump` | | | |
| Checksum | SHA256 no `.meta.txt` conferido | | | |
| Comando restore | Documentado; testado só em clone | | | |

## Smoke pós-migração (lote inicial)

### Receção

- [ ] Pesquisar utente importado
- [ ] Abrir ficha e ver aviso de dados importados
- [ ] Actualizar telefone/residência
- [ ] Confirmar dados (provenance mantém-se)
- [ ] Continuar atendimento (consulta/fila) sem bloquear por campos em falta

### Médico

- [ ] Abrir utente importado
- [ ] Ver histórico anterior (`PatientHistory`)
- [ ] Distinguir histórico importado de consulta SGCS nova

### Director

- [ ] Receita do dia inalterada
- [ ] Nenhuma fatura histórica como dívida activa
- [ ] Caixa/saldos iguais ao pré-import

### Laboratório

- [ ] Histórico textual visível
- [ ] Sem fingir resultado estruturado / pedido moderno

## Stop

Parar se checksum Excel divergir, backup falhar, dry-run ≠ 156/182, leakage financeiro/stock, rollback dry-run tocar objectos externos, provenance ausente, órfãos, ou `--reviewed-only` com `SAUVIDA-HIST-V1`.
