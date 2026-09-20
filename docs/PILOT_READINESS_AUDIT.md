# Auditoria — Prontidão do piloto SGCS SauVida

**Data:** 2026-08-25  
**Âmbito:** auditoria de integração e readiness (sem novas funcionalidades)  
**Perfis base:** Receção · Médico · Laboratório · Enfermagem · Director → `*_READY_FOR_UAT`  
**Estado:** `PILOT_READY_FOR_UAT` (com bloqueios de **go-live com dados reais** listados abaixo)

---

## Veredicto

O produto está **pronto para UAT presencial integrado** num ambiente **demo/LAN controlado**, com suite verde e fluxos por perfil endurecidos (Sprints 23–27).

**Não** está automaticamente **GO** para operação com dados clínicos reais sem:

1. HTTPS activo no host piloto;
2. backup PostgreSQL **real** (não stub da API Settings);
3. impressão validada na impressora da clínica;
4. contactos preenchidos no plano de contingência;
5. `seed_demo` **nunca** corrido na BD piloto real.

---

## 1. Integração E2E (evidência)

| Fluxo | Evidência principal | Estado auditoria |
|---|---|---|
| Walk-in Receção → médico | `test_reception_e2e_uat.py`, `test_reception_doctor_assignment.py` | API OK |
| Triagem enfermagem → vitais no prontuário | Sprint 26 + `sinais_vitais_triagem` | API OK |
| Médico SOAP / pedido lab → regularização Receção | Sprint 24/25 tests | API OK |
| Lab bloqueado até regularizar → validar → médico vê | Sprint 25 + filtro resultados médico | API OK |
| Pagamentos integral/parcial/redução | Sprint 23.x billing + resumo operacional | API OK |
| Stock enfermagem; Director/Médico RO; Receção sem acesso | Sprint 26 + nav | API/RBAC OK |
| Director agregados sem `reception.view` | Sprint 27 | API OK |
| Histórico migrado isolado de faturação | Sprint 21 Fase 4 + resumo | Confirmado |

**Lacuna UAT:** não há teste browser E2E automatizado único «Receção→…→Director»; a prova presencial está em `UAT_PILOTO_SAUVIDA_MASTER.md`.

---

## 2. RBAC cross-role (matriz resumida)

| Acção | REC | ENF | MED | LAB | DIR | ADM |
|---|---|---|---|---|---|---|
| Faturar / pagar | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Triagem / stock write | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| SOAP / diagnóstico / Rx | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ |
| Validar resultado lab | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ |
| Ver valores lab clínicos | ✗ | ✗ | ✓* | ✓ | ✗ | ✓ |
| Stock read | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |
| Relatórios / painel exec. | parcial | — | — | — | ✓ | ✓ |
| Users / settings / seed | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |

\*Médico: só `VALIDADO` / `ENTREGUE`.

Redirect login: `getRoleDashboardPath` → dashboards por perfil (incl. enfermeiro `/dashboard/nurse`).

---

## 3. Dados demo

Fonte: `seed_demo` + `docs/DEMO_DATA.md`.

| Item | Presente? |
|---|---|
| Admin, Director, 2 médicos, Receção, Lab, Enfermeiro | Sim |
| Pacientes fictícios | Sim (6) |
| Serviço / fatura / pagamento | Sim (actor Receção após Sprint 28) |
| Consultas + fila | Sim |
| Pedido lab | Sim (1) |
| Stock urgência | **Não** — criar no UAT Enfermagem |
| Nomes reais | Não (fictícios / DEMO-*) |

Reset: ver `DEMO_DATA.md`. **Proibido** em BD piloto real.

---

## 4. Infraestrutura

| Componente | Achado |
|---|---|
| Docker Compose | `db`, `redis`, `backend`, `celery-worker`, `celery-beat`, `frontend` |
| Healthchecks | db/redis/backend (`/ready/`); celery/frontend **sem** healthcheck dedicado |
| Settings produção | `production.py`: `DEBUG=False`, cookies secure, HSTS; `SECURE_SSL_REDIRECT` **opt-in** |
| Compose actual | `DJANGO_SETTINGS_MODULE=development` — adequado a demo, **não** a piloto público |
| Reverse proxy / TLS | **Não** incluído no compose; obrigatório fora do compose para dados reais |
| Redis / Celery | Presentes; tarefas de backup Settings = **stub** (`tamanho_bytes=0`) |
| Backup operacional | `pg_dump` via `docker exec sgcs-db` documentado (`MIGRACAO_HISTORICA_BACKUP.md`) |
| Logs | `production.py` pode activar ficheiros JSON; validar ausência de tokens em claro no UAT |

---

## 5. Segurança / privacidade

| Tema | Estado |
|---|---|
| JWT access/refresh + rotate | Configurado (`SIMPLE_JWT`); FE com fila de refresh |
| Clinical privacy Receção | Sprint 23.3 — sem SOAP/valores lab |
| Director sem clinical write / lab results.view | Sprint 27 |
| PatientHistory ≠ Fatura/Pagamento | Confirmado |
| Secrets em Git | `.env.example` sem secrets reais; `.env` gitignored |

---

## 6. Impressão

Documentos existentes (recibo, resultado lab, receita se UI disponível) — **código** com fluxo `?imprimir=1`.  
Validação A4 / impressora física / margens / logo: **pendente UAT presencial** (`UAT_RECIBO_SAUVIDA.md` + master).

---

## 7. Performance

Metas em `UAT_TEMPOS_ALVO.md`. Medição informal neste sprint: **não executada em rede clínica**.  
Registar na sessão presencial; só optimizar se desvio > 50% da meta.

---

## 8. Continência

`PLANO_CONTINGENCIA_CLINICA.md` cobre internet, energia, servidor, impressora, sessão, pagamento.  
**Completar:** contactos; secções explícitas «médico indisponível» e «lab parado» na sessão de briefing (procedimento papel já implícito).

---

## 9. Erros UI

- `NotFoundPage` (404)
- `ErrorBoundary` (erros React)
- Dashboards Director com isolamento parcial de falhas
- Sem traceback esperado na UI de produção (`DEBUG=False`)

---

## 10. Bloqueios go-live (não bloqueiam início do UAT demo)

| ID | Severidade | Descrição |
|---|---|---|
| B-01 | P0 | API Settings backup = stub; usar `pg_dump` real + checksum + cópia off-server |
| B-02 | P0 | HTTPS / `SECURE_SSL_REDIRECT` não activos no compose de desenvolvimento |
| B-03 | P1 | Impressão física ainda não assinada na clínica |
| B-04 | P2 | `seed_demo` sem stock; demo lab não cobre AGUARDA_REGULARIZACAO completo |
| B-05 | P2 | Contactos contingência por preencher |

---

## Gates técnicos (Sprint 28)

Ver `SPRINT28_PILOT_READINESS_REPORT.md`.
