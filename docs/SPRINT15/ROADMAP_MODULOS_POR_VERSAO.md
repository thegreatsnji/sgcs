# Roadmap de módulos por versão (pós-Sprint 15)

Reorganização após visita à clínica SauVida. **Sprints 1–14 entregues.** Sprint 15 = análise e dados; **sem** módulos completos de Farmácia, Cirurgia ou Maternidade.

---

## Legenda de estado

| Símbolo | Significado |
|---------|-------------|
| ✅ | Entregue e em produção / demo |
| 📋 | Especificado na Sprint 15; desenvolvimento pendente |
| 🚫 | Explicitamente fora do âmbito imediato |
| 🔮 | Visão futura |

---

## v1.0 – v1.2 (concluído)

| Versão | Conteúdo | Estado |
|--------|----------|--------|
| **1.0** | Auth, RBAC, utilizadores, dashboard, pacientes | ✅ |
| **1.1** | Receção, agenda, consultas, PCE | ✅ |
| **1.2** | Laboratório, faturação, financeiro, relatórios, settings, médico, notificações, produção, UI/UX (S14) | ✅ |

---

## v1.3 — Arranque clínico (Sprint 15 + hardening)

| Entrega | Tipo | Estado |
|---------|------|--------|
| Validação fluxos reais | Documentação | 📋 Sprint 15 |
| Catálogo serviços/preços FCFA | Dados + `import_servico_catalog` | 📋 Sprint 15 |
| Perfil e departamentos iniciais | Dados + `seed_clinic_initial` | 📋 Sprint 15 |
| Lacunas e roadmap actualizado | Documentação | 📋 Sprint 15 |

**Não inclui** novos apps Django para departamentos clínicos.

---

## v1.3.1 — Go-live hardening (próxima sprint de código)

| Módulo / item | Estado |
|---------------|--------|
| UI cancelamento consulta | 📋 |
| Ligação impressões (fatura, recibo, receita, lab) | 📋 |
| Recuperação palavra-passe | 📋 |
| Notificação lab publicada (canal acordado) | 📋 |
| UAT com checklist ENTREVISTAS sec. 6 | 📋 |

---

## v1.4 — Enfermagem e triagem

| Âmbito | Estado |
|--------|--------|
| Perfil enfermeiro / triagem | 📋 SRS pendente |
| Fila clínica pós-triagem | 📋 |
| Sinais vitais fora da consulta | 📋 |
| Integração com receção e fila | 📋 |

🚫 Sem farmácia nesta versão.

---

## v1.5 — Imagiologia, ecografia e lab alargado

| Âmbito | Estado |
|--------|--------|
| Agenda/fila ecografia | 📋 |
| Laudos e anexos | 📋 |
| Catálogo exames lab/imunologia alinhado ao preçário | 📋 |
| Pedidos desde consulta (extensão PCE) | 📋 |

---

## v1.6 — Farmácia (fase 1)

| Âmbito | Estado |
|--------|--------|
| Dispensação ligada a prescrição | 🚫 até SRS |
| Stock e entradas | 🚫 |
| Preços medicamentos | Parcial via `Servico` até lá |

---

## v1.7 — Cirurgia

| Âmbito | Estado |
|--------|--------|
| Lista cirúrgica, bloco, materiais | 🚫 até SRS |
| Faturação procedimentos | Parcial via catálogo PROCEDIMENTO |

---

## v1.8 — Maternidade, obstetrícia e parteira

| Âmbito | Estado |
|--------|--------|
| Pré-natal estruturado | 🚫 até SRS |
| Parto / parteira | 🚫 |
| Ligação internamento | v1.9 |

---

## v1.9 — Internamento e camas

| Âmbito | Estado |
|--------|--------|
| Ocupação de camas | 🚫 até SRS |
| Diárias automáticas na faturação | 📋 conceito em catálogo INTERNAMENTO |

---

## v2.0+ (inalterado)

Portal do paciente, mobile, BI avançado, integrações — ver [PRODUCT_ROADMAP.md](../SRS/PRODUCT_ROADMAP.md).

---

## Mapa módulo → app Django actual

| Área clínica | App / notas |
|--------------|-------------|
| Pacientes | `patients` |
| Receção / fila | `reception` |
| Consultas / PCE | `appointments` |
| Médico (prescrições, alta) | `doctors` |
| Laboratório | `laboratory` |
| Faturação (catálogo) | `billing` |
| Financeiro | `finance` |
| Enfermagem | *não existe* → v1.4 |
| Imagiologia | *parcial* `appointments` imaging → v1.5 |
| Farmácia / Cirurgia / MAT / Internamento | *não existe* → v1.6–v1.9 |

---

*Aprovação da direcção clínica necessária antes de abrir sprint de código para v1.4+.*
