# Sprint 20 — Relatório UAT e preparação piloto

**Data:** 2026-08-02  
**Projecto:** SGCS — Clínica SauVida  
**Âmbito:** Documentação UAT, formação, ambiente piloto, contingência — **sem novos módulos** nem alteração de API/RBAC.

---

## 1. Sessões realizadas

| Sessão | Perfil | Estado |
|--------|--------|--------|
| S1 | Rececionista | **PLANEADA** — ficha [UAT_RECECAO_PRESENCIAL.md](UAT_RECECAO_PRESENCIAL.md) |
| S2 | Médico 1 | **PLANEADA** — [UAT_MEDICO_PRESENCIAL.md](UAT_MEDICO_PRESENCIAL.md) |
| S3 | Médico 2 | **PLANEADA** — idem |
| S4 | Laboratório | **PLANEADA** — [UAT_LABORATORIO_PRESENCIAL.md](UAT_LABORATORIO_PRESENCIAL.md) |
| S5 | Director | **PLANEADA** — [UAT_DIRECTOR_PRESENCIAL.md](UAT_DIRECTOR_PRESENCIAL.md) |
| S6 | Administrador | **PLANEADA** — [PILOT_ENVIRONMENT_CHECKLIST.md](PILOT_ENVIRONMENT_CHECKLIST.md) |

**Nota:** A Sprint 20 **preparou** o pacote UAT e gates técnicos. As sessões **presenciais na clínica** devem ser agendadas e os campos «Obtido/Estado» preenchidos nos documentos.

Plano mestre: [UAT_PLANO_SAUVIDA.md](UAT_PLANO_SAUVIDA.md)

---

## 2. Utilizadores participantes

| Perfil | Nome (preencher) | Data sessão |
|--------|------------------|-------------|
| Rececionista | | |
| Médico 1 | | |
| Médico 2 | | |
| Técnico laboratório | | |
| Director | | |
| Administrador | | |

---

## 3–7. Casos testados (consolidado)

| Área | Casos definidos | Executados presencialmente | Aprovados | Falhados | Bloqueados |
|------|----------------:|---------------------------:|----------:|---------:|-----------:|
| Recepção | 20 + 10 específicos | 0 | 0 | 0 | 0 |
| Médico | 13 | 0 | 0 | 0 | 0 |
| Laboratório | 11 + filtros | 0 | 0 | 0 | 0 |
| Director | 13 | 0 | 0 | 0 | 0 |
| **Total definido** | **~67** | **0** | **0** | **0** | **0** |

**Evidência técnica pré-UAT:** regressão automatizada **315** testes (ver secção 13).

---

## 8. Problemas críticos

| ID | Descrição | Estado |
|----|-----------|--------|
| — | Nenhum CRÍTICO aberto em código na Sprint 20 | — |

Registo vivo: [UAT_ISSUES_SAUVIDA.md](UAT_ISSUES_SAUVIDA.md) (UAT-001 impressão física — validar na sessão).

---

## 9. Problemas corrigidos na Sprint 20

Nenhuma alteração de código aplicável (apenas documentação e processo). Correcções de bloqueios serão feitas **após** UAT presencial conforme Parte 8.

---

## 10. Tempos medidos

Metas: [UAT_TEMPOS_ALVO.md](UAT_TEMPOS_ALVO.md)

| Métrica | Meta | Medido na clínica |
|---------|-----:|------------------:|
| Atendimento simples recepção | ≤ 2 min | *pendente* |
| Emissão recibo | ≤ 30 s | *pendente* |
| Pesquisa paciente | ≤ 2 s | *pendente* |
| Abertura consulta | ≤ 3 s | *pendente* |

---

## 11. Formação

| Documento | Estado |
|-----------|--------|
| [FORMACAO_RECECAO.md](FORMACAO_RECECAO.md) | Publicado |
| [FORMACAO_MEDICO.md](FORMACAO_MEDICO.md) | Publicado |
| [FORMACAO_LABORATORIO.md](FORMACAO_LABORATORIO.md) | Publicado |
| [FORMACAO_DIRECTOR.md](FORMACAO_DIRECTOR.md) | Publicado |

**Formação presencial:** pendente de sessão de 30 min na recepção.

---

## 12. Ambiente piloto

Checklist: [PILOT_ENVIRONMENT_CHECKLIST.md](PILOT_ENVIRONMENT_CHECKLIST.md)

| Item | Estado Sprint 20 |
|------|------------------|
| Dev local + catálogo V1 | Validado em desenvolvimento |
| VPS / HTTPS produção piloto | **Pendente** assinatura clínica |
| Backups piloto | Procedimento documentado; repetir no host piloto |
| Impressora clínica | **Pendente** teste R17 |

---

## 13. Contingência

[PLANO_CONTINGENCIA_CLINICA.md](PLANO_CONTINGENCIA_CLINICA.md) — publicado; contactos a preencher na clínica.

---

## 14. Testes automatizados

| Gate | Resultado | Log |
|------|-----------|-----|
| `manage.py check` | OK | `docs/logs/sprint20_manage_check.txt` |
| `makemigrations --check` | OK | `docs/logs/sprint20_migrations.txt` |
| `pytest -q --reuse-db` | **315 passed** | `docs/logs/sprint20_pytest.txt` |

---

## 15. Build e lint

| Gate | Resultado | Log |
|------|-----------|-----|
| `npm run build` | OK | `docs/logs/sprint20_build.txt` |
| `npm run lint` | 0 erros | `docs/logs/sprint20_lint.txt` |

---

## 16. Critérios de aprovação (Parte 12)

| Critério | Estado |
|----------|--------|
| Nenhum erro crítico aberto | OK (código) |
| Recepção fluxo completo | **Pendente UAT presencial** |
| Médico consulta completa | **Pendente** |
| Lab. publicar resultado | **Pendente** |
| Director indicadores | **Pendente** |
| Recibo / reduções / parciais | Coberto por testes auto.; **impressão pendente** |
| Catálogo V1 | OK em dev |
| Backups validados no piloto | **Pendente** |
| HTTPS piloto | **Pendente** |
| Formação utilizadores | Material pronto; sessão pendente |
| Gates verdes | **OK** |

---

## 17. Decisão final

### **APROVADO COM RESSALVAS**

**Ressalvas:**

1. UAT presencial **não executado** nesta sprint — apenas planeado e documentado.  
2. Ambiente piloto (HTTPS, VPS, impressora, backups no host) **por validar** na clínica.  
3. Tempos-alvo **por medir** em [UAT_TEMPOS_ALVO.md](UAT_TEMPOS_ALVO.md).

**Não é ainda «APROVADO PARA PILOTO» em produção** até concluir sessões S1–S6 e fechar issues CRÍTICO/ALTO.

---

## Próximos passos obrigatórios

1. Agendar **S1 Recepção** (2–3 h) com portátil e impressora reais.  
2. Preencher tabelas UAT e actualizar [UAT_ISSUES_SAUVIDA.md](UAT_ISSUES_SAUVIDA.md).  
3. Completar [PILOT_ENVIRONMENT_CHECKLIST.md](PILOT_ENVIRONMENT_CHECKLIST.md) no servidor piloto.  
4. Sessão formação 30 min (recepção) + distribuir manuais.  
5. Corrigir apenas bloqueios; re-executar casos falhados + `pytest`.  
6. Reunião go/no-go com Director — decisão final **APROVADO PARA PILOTO** ou **REPROVADO**.
