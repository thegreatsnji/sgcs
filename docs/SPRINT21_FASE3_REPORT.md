# Sprint 21 Fase 3 — Relatório

**Projecto:** SGCS — Clínica SauVida  
**Data:** 2026-08-17  
**Batch:** `SAUVIDA-HIST-V1`  
**Estado final:** `IMPORTACAO_PARCIAL_CONCLUIDA`

## 1. Ambiente

Docker Compose local, `APP_ENV=development`, `DEBUG=true`. PostgreSQL 16, BD `sgcs` no contentor `sgcs-db`. **Não é produção clínica.** Actor: `admin@sauvida.gw` (Administrador activo).

## 2. Backup

Dump PostgreSQL real via `docker exec sgcs-db pg_dump` (o `manage.py backup_sauvida_pre_apply` falha dentro de `sgcs-backend` por falta de `pg_dump`/`docker`).

Ficheiro: `backups/pre_sauvida_hist/sgcs_pre_sauvida_hist_20260817_152144.sql`  
Tamanho: **499108** bytes  
Pasta `backups/` gitignored. Sem credenciais no log.

## 3. Checksum

SHA256: `6c8fdb901bb373b2f602dda359b1dd0abedd279aedde3a548914e87879daebc0`

## 4. Dry-run final

156 pacientes prontos, 38 bloqueados, 182 eventos prontos, 66 bloqueados, 173 órfãos, 55 stock não processados. Sobreposição prontos/bloqueados = 0. Ver `docs/logs/sprint21_fase3_dry_run_final.txt`.

## 5. Pacientes importados

156 criados. 0 actualizados. Proveniência `MIGRACAO_EXCEL_SAUVIDA`, batch `SAUVIDA-HIST-V1`, `migration_id` únicos, `dados_verificados=false`.

## 6. Pacientes bloqueados

38 intactos, nenhum importado. 23 pares de duplicados **não** resolvidos automaticamente.

## 7. Auditoria dos pacientes

Aprovada. Ver `docs/SPRINT21_FASE3_PATIENTS_AUDIT.md`. Pacientes incompletos utilizáveis. ids 1–10 SGCS intactos.

## 8. Idempotência

Caminho de apply reutiliza por `migration_id`: **0** novos a criar. Dry-run de staging ainda lista 151+5 porque 5 utentes fazem `SAFE_MATCH` consigo próprios; apply não funde nem duplica.

## 9. Eventos importados

182 clínicos. Nenhum extra financeiro `KIND`.

## 10. Eventos bloqueados

66 intactos. 173 sem paciente não importados. 4 datas bloqueadas não importadas.

## 11. Histórico por tipo

111 consultas · 16 controlos · 4 laboratório estruturado · 39 laboratório textual · 8 ecografias · 4 cirurgias.

## 12. Financeiro histórico

182 valores só em metadata de `PatientHistory`. Receita, caixa, saldo, pagamentos do dia, recibos e cobranças activas **inalterados** (relatórios leem `Fatura`/`Pagamento`/`Recibo`/`MovimentoFinanceiro`).

## 13. Laboratório histórico

Textual e estruturado conforme staging. Sem pedidos/resultados modernos inventados.

## 14. Médicos históricos

3 não mapeados. `medico_sgcs` nulo. Sem contas criadas.

## 15. Stock

Não importado (55 candidatos, `quantidade_inicial` vazia).

## 16. Contagens BD

Ver `docs/SPRINT21_FASE3_DB_COUNTS.md`. Patient 10→166. PatientHistory 10→348. Restantes tabelas operacionais iguais.

## 17. Rollback dry-run

338 históricos e 156 pacientes do lote identificados. `escrita_bd=false`. Dados fora do batch não visados. Rollback real **não** executado.

## 18. Testes

`apps/data_migration/tests/`: 33 passed.  
Suite: **352 passed**, **2 failed** pré-existentes na Receção (médico indisponível). Receção **não** alterada.

## 19. Gates

- `manage.py check`: OK (0 problemas)
- `makemigrations --check`: OK (sem alterações)
- Frontend: não alterado nesta fase (lint/build da Fase 2 mantêm-se)

## 20. Problemas

- `backup_sauvida_pre_apply` não corre dentro do contentor backend; backup feito pelo equivalente `docker exec sgcs-db pg_dump`.
- Dry-run após importação de pacientes não desconta `migration_id` já existentes (não causa duplicados no apply).

## 21. Riscos

- 38 pacientes e 66 eventos continuam fora do SGCS até decisão clínica (duplicados, datas, labs ambíguos).
- 173 eventos sem paciente permanecem só em arquivo CSV.
- Montantes históricos visíveis na cronologia clínica se a UI mostrar metadata; não entram na faturação.
- Confirmação «Confirmar dados» ainda pendente para os 156 utentes (`dados_verificados=false`).

## 22. Estado final

**IMPORTACAO_PARCIAL_CONCLUIDA**
