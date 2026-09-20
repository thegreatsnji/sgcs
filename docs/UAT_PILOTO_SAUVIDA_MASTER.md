# UAT Piloto SauVida — Master

**Objectivo:** sessão(ões) presencial(is) de integração, sem duplicar os UAT por perfil.  
**Estado produto:** `PILOT_READY_FOR_UAT`  
**Critérios de marcação:** `PASSOU` | `PASSOU COM DIFICULDADE` | `FALHOU`  
Registar sempre: **tempo (min)**, **observação**, **precisou de ajuda? (S/N)**.

---

## Documentos por perfil (executar na íntegra ou amostragem)

| Perfil | Documento | Prioridade |
|---|---|---|
| Receção | [UAT_RECEPCIONISTA_FINAL.md](UAT_RECEPCIONISTA_FINAL.md) | Essencial |
| Médico | [UAT_MEDICO_FINAL.md](UAT_MEDICO_FINAL.md) | Essencial |
| Laboratório | [UAT_LABORATORIO_FINAL.md](UAT_LABORATORIO_FINAL.md) | Essencial |
| Enfermagem | [UAT_ENFERMAGEM_FINAL.md](UAT_ENFERMAGEM_FINAL.md) | Essencial |
| Director | [UAT_DIRECTOR_FINAL.md](UAT_DIRECTOR_FINAL.md) | Essencial |
| Recibo | [UAT_RECIBO_SAUVIDA.md](UAT_RECIBO_SAUVIDA.md) | Essencial se impressora |
| Tempos | [UAT_TEMPOS_ALVO.md](UAT_TEMPOS_ALVO.md) | Medir amostragem |
| Ambiente | [PILOT_ENVIRONMENT_CHECKLIST.md](PILOT_ENVIRONMENT_CHECKLIST.md) | Antes do dia 1 |
| Contingência | [PLANO_CONTINGENCIA_CLINICA.md](PLANO_CONTINGENCIA_CLINICA.md) | Briefing |

---

## Dia 0 — Preparação

| # | Tarefa | Resultado | Tempo | Ajuda | Obs. |
|---|---|---|---|---|---|
| P1 | `migrate` + `seed_rbac` (+ `seed_demo` **só se BD demo**) | | | | |
| P2 | Login dos 7 perfis → dashboard correcto | | | | |
| P3 | Catálogo serviços operacional visível | | | | |
| P4 | Impressora ligada; teste página | | | | |
| P5 | Briefing contingência + contactos | | | | |

Redirect esperado: Admin `/dashboard/admin` · Director `/dashboard/director` · Médico `/dashboard/doctor` · Receção `/dashboard/reception` · Lab `/dashboard/laboratory` · Enfermeiro `/dashboard/nurse`.

---

## Dia 1 — Fluxo clínico integrado (obrigatório)

Um único utente **fictício** percorre a cadeia. **Não** recriar paciente/consulta/pedido/fatura entre passos.

| # | Passo | Perfil | Resultado | Tempo | Ajuda | Obs. |
|---|---|---|---|---|---|---|
| I1 | Registar/pesquisar utente + atendimento | Receção | | | | |
| I2 | Serviço → faturar → pagar (integral ou parcial) | Receção | | | | |
| I3 | Atribuir médico | Receção | | | | |
| I4 | Triagem + vitais + prioridade | Enfermagem | | | | |
| I5 | Abrir consulta atribuída; ver triagem | Médico | | | | |
| I6 | SOAP + diagnóstico + prescrição | Médico | | | | |
| I7 | Pedido laboratório | Médico | | | | |
| I8 | Ver pedido a regularizar; faturar/marcar | Receção | | | | |
| I9 | Processar + resultado + validar + imprimir | Lab | | | | |
| I10 | Ver resultado validado; concluir consulta | Médico | | | | |
| I11 | Painel: faturado/recebido/saldo coerentes | Director | | | | |

**Falha se:** passo exigir recriar entidade; lab processar sem regularizar; médico ver valores antes de validar; Receção ver valores clínicos; Director executar caixa.

---

## Dia 1 — Variantes rápidas

| # | Cenário | Resultado | Tempo | Ajuda | Obs. |
|---|---|---|---|---|---|
| V1 | Walk-in sem marcação até consulta | | | | |
| V2 | Marcação → confirmar chegada → check-in → fatura → médico (sem duplicados) | | | | |
| V3 | Paciente histórico importado: provenance + nova consulta SGCS sem alterar histórico | | | | |
| V4 | Pagamento parcial + 2.º pagamento; overpay bloqueado; cancelar fatura | | | | |
| V5 | Redução (+ parcial se aplicável) | | | | |
| V6 | Lab AGUARDA_REGULARIZACAO bloqueia start | | | | |
| V7 | Stock: inicial/entrada/saída/ajuste/perda; expirado bloqueia saída | | | | |
| V8 | Director/Médico stock RO; Receção sem stock | | | | |

---

## Segurança / erros (amostra)

| # | Tarefa | Resultado | Obs. |
|---|---|---|---|
| S1 | Matriz 403: cada perfil tenta acção proibida | | |
| S2 | Rota inexistente → 404 amigável | | |
| S3 | Logout / refresh / token expirado sem loop | | |
| S4 | Rede lenta / refresh: dados já guardados persistem | | |

---

## Devices

| Device | Usado? | Perfis testados | Obs. |
|---|---|---|---|
| Chrome desktop | | | |
| Portátil Receção | | | |
| Tablet | | | |
| Telemóvel Director (~390px) | | | |

---

## Severidade de issues

| Código | Severidade | Descrição | Estado |
|---|---|---|---|
| | P0 / P1 / P2 / P3 | | Aberto / Contornado / Fechado |

---

## Decisão do dia

- [ ] Continuar UAT  
- [ ] Pausar (P0/P1)  
- [ ] Pronto para checklist GO/NO-GO (`PILOT_GO_NO_GO_CHECKLIST.md`)

**Assinaturas:** Receção ______ Médico ______ Lab ______ Enf. ______ Director ______ Data ______
