# Matriz de verificação por área clínica

**SGCS** — estado após Sprints 1–14 + Sprint 15 (dados/documentação)  
**Legenda:** ✅ Implementado · ⚠️ Parcial · ❌ Não existe · 📋 Apenas catálogo/config (sem módulo)

---

## Resumo

| Área | Situação global | Versão alvo |
|------|-----------------|-------------|
| Receção | ⚠️ (faturação fora do perfil receção por defeito) | v1.3.1 |
| Enfermagem | ⚠️ (triagem na receção; sem módulo enfermagem) | v1.4 |
| Laboratório | ⚠️ (preço via `Servico`, não no tipo de exame) | v1.5 |
| Ecografia | ⚠️ (pedido PCE; sem agenda/laudo) | v1.5 |
| Maternidade | 📋 / ❌ | v1.8 |
| Cirurgia | 📋 / ❌ | v1.7 |
| Medicamentos de urgência | ❌ | v1.6 |
| Serviços | ✅ / ⚠️ | Sprint 15 |
| Faturação | ⚠️ (manual por linha `Servico`) | contínuo |
| RBAC | ✅ / ⚠️ | ajustes por política |
| Relatórios | ⚠️ (por serviço; não por departamento) | v1.5+ |

---

## 1. Receção

| Verificar | Estado | Evidência / notas |
|-----------|:------:|-------------------|
| Pacientes (registo, pesquisa) | ✅ | `patients` + RBAC `patients.*` para receção |
| Marcações / agenda | ✅ | `appointments` — criar, confirmar, cancelar (API; UI cancelamento ⚠️) |
| Fila de espera | ✅ | `reception` — check-in, fila, prioridade, encaminhamento |
| Faturação | ⚠️ | Módulo `billing` existe; **rececionista por defeito não tem** `billing.*` (`seed_rbac`) nem menu `/billing` |
| Pagamentos | ⚠️ | Idem — normalmente **Director** (ou permissões extra à receção) |
| Recibos | ⚠️ | Idem — `billing.receipt` no Director |

**Acção:** Se a receção deve cobrar no balcão, acrescentar `billing.view/create/payment/receipt` ao perfil RECECIONISTA (política + UAT).

---

## 2. Enfermagem

| Verificar | Estado | Evidência / notas |
|-----------|:------:|-------------------|
| Triagem | ⚠️ | **Receção:** `TriageCheckInWizard`, cor de triagem, PA, sintomas (`reception` migration `triage_fields`) — não é app “Enfermagem” |
| Sinais vitais | ⚠️ | **Consulta/PCE:** `POST …/vital-signs/` (médico/clinical); triagem guarda PA no check-in |
| Observações | ⚠️ | Check-in / fila / PCE SOAP — sem prontuário de enfermagem dedicado |
| Procedimentos (curativos, nebulização, etc.) | ❌ | Só como linhas **PROCEDIMENTO** no catálogo CSV; sem registo clínico de execução |
| Perfil ENFERMEIRO | ⚠️ | Role existe; permissões mínimas (`patients.view`, `appointments.view/edit`); **sem menu/UI própria** |

**Acção:** v1.4 — SRS enfermagem + triagem (unificar ou separar da receção).

---

## 3. Laboratório

| Verificar | Estado | Evidência / notas |
|-----------|:------:|-------------------|
| Pedidos | ✅ | Consulta → `PedidoLaboratorial`; workflow completo |
| Catálogo (tipos de exame) | ✅ | `settings.TipoExameLaboratorio` (sem preço) |
| Preços | ⚠️ | **Faturação:** `billing.Servico` + CSV Sprint 15; alinhar códigos `EX-LAB-*` com tipos de exame |
| Resultados | ✅ | Validar, publicar, anexos, PCE |
| Faturação | ⚠️ | **Manual:** orçamento/fatura com `Servico`; sem auto-linha ao publicar resultado |

**Acção:** Importar catálogo; opcional v1.5 — ligar tipo de exame ↔ `Servico` e sugerir linha na fatura.

---

## 4. Ecografia

| Verificar | Estado | Evidência / notas |
|-----------|:------:|-------------------|
| Pedidos | ⚠️ | `POST …/appointments/{id}/imaging/` + modelo `PedidoImagiologia`; UI indica integração futura |
| Agendamento | ❌ | Sem fila/sala/calendário de ecografia |
| Relatório / laudo | ❌ | Sem módulo de laudo estruturado (só pedido no PCE) |
| Preço | 📋 | Linhas `PROC-ECO-*` no `catalogo_servicos_sauvida.csv` |

**Acção:** v1.5 — módulo imagiologia.

---

## 5. Maternidade

| Verificar | Estado | Evidência / notas |
|-----------|:------:|-------------------|
| Pré-natal | ⚠️ | Consulta GO como consulta geral + `CONS-PRE-NATAL` no catálogo |
| Parto | ❌ | Preço referência `PROC-PARTO-*` no CSV apenas |
| Gestante | ❌ | Sem ficha obstétrica (DUM, IG, risco, etc.) |
| Recém-nascido | ❌ | Sem registo RN ligado à mãe |

**Acção:** v1.8 — não implementar sem SRS.

---

## 6. Cirurgia

| Verificar | Estado | Evidência / notas |
|-----------|:------:|-------------------|
| Procedimentos | 📋 | Catálogo `PROC-CIR-*` |
| Agendamento | ❌ | Sem bloco operatório |
| Equipa | ❌ | Sem modelo cirúrgico |
| Materiais | ❌ | Sem stock OT |
| Faturação | ⚠️ | Via `Servico` PROCEDIMENTO manual |

**Acção:** v1.7.

---

## 7. Medicamentos de urgência

| Verificar | Estado | Evidência / notas |
|-----------|:------:|-------------------|
| Stock interno | ❌ | Sem inventário |
| Uso / consumo | ❌ | Prescrição médica (`doctors`) ≠ dispensação |
| Validade | ❌ | — |
| Consumo registado | ❌ | — |

**Acção:** v1.6 farmácia/stock; urgência pode ser subconjunto.

---

## 8. Serviços (catálogo central)

| Verificar | Estado | Evidência / notas |
|-----------|:------:|-------------------|
| Catálogo central | ✅ | `billing.Servico` |
| Categorias | ✅ | CONSULTA, EXAME, PROCEDIMENTO, INTERNAMENTO, OUTRO |
| Departamentos | ⚠️ | `settings.Departamento` + `departamentos_sauvida.json` — **não ligado** a `Servico` |
| Preços | ⚠️ | CSV Sprint 15 + `import_servico_catalog` — validar valores reais |

---

## 9. Faturação (integração transversal)

| Verificar | Estado | Evidência / notas |
|-----------|:------:|-------------------|
| Consultas | ⚠️ | Linha manual `Servico` CONSULTA |
| Laboratório | ⚠️ | Manual; sem trigger automático |
| Ecografia / cirurgia / maternidade | ⚠️ / 📋 | Catálogo; sem workflow |
| Farmácia | ❌ | Taxa `OUT-FARM-MARGEM` no CSV apenas |
| Pagamento → caixa | ✅ | Billing → Finance (entrada confirmada) |

---

## 10. RBAC (acesso por perfil)

| Perfil | Áreas típicas | Notas |
|--------|---------------|-------|
| RECECIONISTA | Pacientes, consultas, receção/fila, notificações | **Sem billing** por defeito |
| MEDICO | PCE, lab (ver resultados), prescrições | Sem billing/finance |
| LABORATORIO | Lab + resultados | Sem billing |
| DIRECTOR | Billing, finance, relatórios, amplo clínico | Papel financeiro efectivo |
| ADMINISTRADOR | Tudo + settings | — |
| ENFERMEIRO | Muito limitado | Sem triagem dedicada no menu |

Fonte: `seed_rbac.py`, `navigation.ts`, `docs/ROLE_DASHBOARDS.md`.

---

## 11. Relatórios

| Verificar | Estado | Evidência / notas |
|-----------|:------:|-------------------|
| Receita por serviço | ✅ | `servicos_vendidos` / `top_servicos` (`ItemFatura` × `Servico`) |
| Receita por departamento | ❌ | `Servico` **não tem** `departamento_id`; relatórios não agrupam por dept. |
| Por área clínica (lab, consultas, etc.) | ⚠️ | Relatórios por **módulo** (lab, billing, appointments), não por departamento SauVida |

**Acção:** Modelar ligação Servico↔Departamento ou dimensão analítica (v1.5+).

---

## Checklist UAT rápido (por área)

Use com [USER_TESTING_GUIDE.md](../USER_TESTING_GUIDE.md):

1. **Receção** — login `rececao@sauvida.gw`: paciente → triagem → fila → consulta; tentar faturar (esperado: negado sem permissão).  
2. **Director** — mesmo fluxo + fatura/pagamento/recibo.  
3. **Lab** — pedido da consulta → resultado publicado.  
4. **Catálogo** — `import_servico_catalog` e ver `/billing/services`.  

---

*Actualizar após alterações de RBAC ou novos módulos.*
