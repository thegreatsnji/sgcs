# Plano de UAT presencial — Clínica SauVida (SGCS)

**Versão:** 1.0 (Sprint 20)  
**Ambiente:** Piloto / pré-produção (não produção activa sem autorização)  
**Catálogo:** SauVida V1 (119 serviços, 87 exames alinhados)  
**Idioma:** Português (PT)

## Objectivo geral

Validar, com utilizadores reais da clínica, que o SGCS suporta o trabalho diário **antes do deploy em produção**, sem novos módulos nem alteração de contratos API.

## Critérios de estado (por caso)

| Estado | Significado |
|--------|-------------|
| **APROVADO** | Comportamento conforme esperado; evidência registada |
| **FALHOU** | Comportamento incorrecto; requer correcção |
| **BLOQUEADO** | Não foi possível testar (ambiente, permissão, hardware) |
| **NECESSITA AJUSTE** | Funciona com ressalva ou UX a melhorar (não bloqueia piloto) |

## Gravidade

| Gravidade | Descrição |
|-----------|-----------|
| CRÍTICO | Impede atendimento ou integridade financeira/clínica |
| ALTO | Fluxo principal degradado sem alternativa aceitável |
| MÉDIO | Incómodo frequente ou risco moderado |
| BAIXO | Cosmético ou raro |
| MELHORIA | Sugestão pós-piloto |

## Sessões planeadas

| Sessão | Perfil | Duração sugerida | Facilitador | Documento de casos |
|--------|--------|------------------|-------------|-------------------|
| S1 | Rececionista | 2–3 h | Coord. implantação | [UAT_RECECAO_PRESENCIAL.md](UAT_RECECAO_PRESENCIAL.md) |
| S2 | Médico 1 | 1,5–2 h | Coord. clínico | [UAT_MEDICO_PRESENCIAL.md](UAT_MEDICO_PRESENCIAL.md) |
| S3 | Médico 2 | 1–1,5 h | Coord. clínico | [UAT_MEDICO_PRESENCIAL.md](UAT_MEDICO_PRESENCIAL.md) |
| S4 | Técnico de Laboratório | 1,5–2 h | Coord. lab. | [UAT_LABORATORIO_PRESENCIAL.md](UAT_LABORATORIO_PRESENCIAL.md) |
| S5 | Director | 45–60 min (incl. telemóvel) | Coord. implantação | [UAT_DIRECTOR_PRESENCIAL.md](UAT_DIRECTOR_PRESENCIAL.md) |
| S6 | Administrador | 1–1,5 h | TI / fornecedor | Checklist piloto + RBAC |

## Modelo de registo por caso

| Campo | Conteúdo |
|-------|----------|
| Objectivo | O que se pretende validar |
| Cenário | Contexto (ex.: utente novo, pagamento parcial) |
| Passos | Sequência executada |
| Resultado esperado | Critério de sucesso |
| Resultado obtido | Preencher na sessão |
| Estado | APROVADO / FALHOU / BLOQUEADO / NECESSITA AJUSTE |
| Observações | Texto livre |
| Gravidade | Se aplicável |
| Responsável | Quem corrige ou valida |
| Evidência | Captura, n.º recibo, hora, operador |

## Pré-requisitos comuns (todas as sessões)

- [ ] Backup da BD piloto validado ([PILOT_ENVIRONMENT_CHECKLIST.md](PILOT_ENVIRONMENT_CHECKLIST.md))
- [ ] Contas de teste ou contas reais com RBAC correcto
- [ ] Catálogo V1 aplicado; legado oculto na receção (`operacional=1`)
- [ ] Portátil / telemóvel da clínica na rede piloto
- [ ] Impressora de teste configurada
- [ ] Formação rápida ([FORMACAO_*.md](FORMACAO_RECECAO.md))
- [ ] [PLANO_CONTINGENCIA_CLINICA.md](PLANO_CONTINGENCIA_CLINICA.md) impresso ou offline

## Pós-UAT

1. Consolidar issues em [UAT_ISSUES_SAUVIDA.md](UAT_ISSUES_SAUVIDA.md)
2. Corrigir apenas bloqueios ([SPRINT20_UAT_REPORT.md](SPRINT20_UAT_REPORT.md) — Parte 8)
3. Re-testar casos falhados
4. Decisão: APROVADO PARA PILOTO / COM RESSALVAS / REPROVADO

## Calendário (preencher na clínica)

| Sessão | Data | Hora | Local | Participantes | Assinatura |
|--------|------|------|-------|---------------|------------|
| S1 Recepção | | | | | |
| S2 Médico 1 | | | | | |
| S3 Médico 2 | | | | | |
| S4 Laboratório | | | | | |
| S5 Director | | | | | |
| S6 Administrador | | | | | |
