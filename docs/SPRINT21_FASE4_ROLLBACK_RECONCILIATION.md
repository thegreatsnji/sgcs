# Sprint 21 Fase 4 — Reconciliação do rollback (338 vs 182)

**Lote:** `SAUVIDA-HIST-V1`  
**Rollback real:** não executado  
**Conclusão:** **não é um bug**. O dry-run conta todos os `PatientHistory` do lote, não só os 182 actos clínicos do Excel.

## Equação

```
338 PatientHistory do lote
  = 156 REGISTO (criados ao importar cada utente)
  + 182 eventos clínicos (consultas, controlos, labs, ecos, cirurgias)
  + 0 registos financeiros extra (KIND)
```

Os 182 valores financeiros históricos estão **dentro** dos 182 eventos clínicos (`metadata.preco_original` / `valor_liquido_original`), não como linhas adicionais.

## Tabela

| Tipo de objecto | Criado no batch | Detectado no rollback | Diferença | Explicação |
| --------------- | --------------: | --------------------: | --------: | ---------- |
| Patient | 156 | 156 | 0 | Utentes importados |
| PatientHistory clínico | 182 | 182 (`historicos_clinicos`) | 0 | Actos do Excel |
| PatientHistory REGISTO | 156 | 156 (`historicos_registo_importacao`) | 0 | Proveniência da criação do utente; entra no rollback para o lote ficar limpo |
| PatientHistory financeiro extra | 0 | 0 | 0 | Valores vão no metadata clínico |
| AuditLog | 156 | 0 (não apagado) | 156 intencional | Trilha forense; rollback **não** apaga auditoria |
| Fatura / Pagamento / Recibo | 0 | 0 | 0 | Fora do âmbito |
| Stock | 0 | 0 | 0 | Fora do âmbito |
| Pacientes SGCS id 1–10 | 0 (pré-existentes) | 0 | 0 | Isolamento confirmado (`historicos_em_pacientes_externos=0`) |

## Dry-run actual (Fase 4)

```
historicos_a_remover: 338
pacientes_a_remover: 156
historicos_registo_importacao: 156
historicos_clinicos: 182
historicos_financeiros_extra: 0
historicos_em_pacientes_externos: 0
escrita_bd: False
```

O comando de rollback foi **enriquecido** com esta decomposição. O total 338 mantém-se: é o conjunto correcto a remover se o lote for revertido.

Critério: o dry-run identifica exactamente os objectos do batch (Patient + PatientHistory do lote) e nenhum objecto externo. **Cumprido.**
