# Dry-run da migração histórica SauVida

**Data:** 2026-08-17  
**Lote:** `SAUVIDA-HIST-V1`  
**Modo:** `--dry-run --skip-blocked`  
**Escrita na BD:** não

Apenas agregados.

## Plano com skip-blocked

| Métrica | Valor |
| --- | --- |
| Pacientes a criar | 156 |
| Pacientes a associar a utentes SGCS | 0 |
| Pacientes bloqueados | 38 |
| Eventos a importar | 182 |
| Eventos bloqueados | 66 |
| Consultas prontas | 111 |
| Controlos prontos | 16 |
| Laboratório estruturado (`ALINHADO`) | 4 |
| Laboratório textual | 39 |
| Ecografias prontas | 8 |
| Cirurgias prontas | 4 |
| Financeiro histórico (valores no histórico clínico) | 182 |
| Datas bloqueadas | 4 |
| Eventos sem paciente (não importar) | 173 |
| Itens ignorados | 491 |
| Médicos não mapeados | 3 |
| Itens de stock a aguardar enfermeira | 55 |

Contagens da BD **inalteradas** no dry-run (Patient 10, PatientHistory 10, User 12, Fatura 5).

`--apply` exige `--confirm-backup` e `--actor-email`. Não foi executado.

## Regras de correspondência

1. processo antigo exacto;
2. telefone + nome compatível;
3. nome + data de nascimento;
4. nome isolado → não fundir;
5. nome semelhante → não fundir.
