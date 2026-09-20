# Auditoria — Pacientes (Receção / RECECIONISTA)

**Data:** 2026-08-20  
**Âmbito:** módulo Pacientes para o perfil RECECIONISTA no SGCS SauVida.  
**Estado:** `PATIENTS_AUDIT_COMPLETE`  
**Código nesta tarefa:** nenhuma alteração (só documentação).

---

## 1. Funcionalidades existentes

### Frontend

| Rota | Página | Menu Receção |
|---|---|---|
| `/patients` | Lista | **Pacientes** (abaixo de Faturação) |
| `/patients/new` | Novo utente | |
| `/patients/:id` | Resumo / ficha | |
| `/patients/:id/edit` | Editar demografia | |
| `/patients/:id/clinical` | Tab «Histórico» (clínico!) | |
| `/patients/:id/documents` | Documentos / fotos | |
| `/patients/:id/history` | Timeline + audit (fora do SubNav) | |

### Backend (principais)

| Endpoint | Permissão Receção | Notas |
|---|---|---|
| `GET/POST /api/v1/patients/` | view / create | Lista + registo |
| `GET/PATCH /api/v1/patients/{id}/` | view / edit | Detalhe / edição administrativa |
| `DELETE …/{id}/` | **delete** — Receção **não tem** | Soft delete |
| `POST …/deactivate/` | delete | Receção **não** |
| `POST …/confirm-imported-data/` | edit | Confirmar dados migrados |
| `GET …/check-duplicate/` | create | Aviso de duplicados |
| Nested allergies / chronic / observations | view / **edit** | **Clínico editável pela Receção** |
| `GET …/history/` | view | PatientHistory (incl. migrado) |
| `GET …/appointments/` | view | Inclui `diagnosis` / `clinical_notes` |

### RBAC RECECIONISTA (seed)

**Tem:** `patients.view`, `create`, `edit`.  
**Não tem:** `patients.delete`, `export`, `print`, `admin`.  
**Não tem:** `laboratory.results.view` → tab Laboratório **oculta**.

---

## 2. Pesquisa (lista)

Campo único: «Pesquisar por nome, documento, telefone ou n.º processo…» → API `search=` sobre:

`full_name`, `first_name`, `last_name`, `document_number`, **`phone`**, **`patient_number`**, `email`.

| Critério | Suportado? |
|---|---|
| Nome | **SIM** |
| Telefone | **SIM** |
| N.º processo / código | **SIM** |
| Documento | **SIM** |

**Filtros:** género; estado (Ativos/Inativos); faixa etária (**só página actual** — parcial).  
**Paginação:** 20 por página.  
**Colunas:** Paciente, N.º Processo, Idade, Género, Telefone, «Última visita» (= `updated_at`, **não** visita real), Estado.  
**Sem** dados clínicos na lista — adequado.

---

## 3. Registar novo utente

Campos no formulário UI:

| Campo | Classificação |
|---|---|
| Nome completo | ESSENCIAL |
| Data de nascimento | ESSENCIAL |
| Género | ESSENCIAL |
| Telefone | ESSENCIAL |
| Grupo sanguíneo | **CLÍNICO** (também útil triagem) |
| Tipo / n.º documento | ÚTIL |
| Morada (rua) | ÚTIL |
| Contactos de emergência | ÚTIL (obrigatório se &lt;18) |

No schema/API mas **não** no formulário UI: email, cidade/região/país, nacionalidade, estado civil, ocupação → OPCIONAL / não expostos no registo.

---

## 4. Duplicação

| Mecanismo | Estado |
|---|---|
| Pesquisa antes do registo | Possível via lista / Atendimento |
| `GET /check-duplicate/` | SIM — documento exacto ou score nome/telefone/nascimento |
| UI `DuplicateAlert` | SIM — aviso âmbar + link «Ver ficha» (create) |
| Bloqueio duro | **NÃO** (só warning) |
| Fuzzy merge / fundir | **NÃO** (correcto) |

**Risco:** telefone vazio + nomes comuns → duplicados possíveis; histórico importado pode coexistir com novo registo se o aviso for ignorado.  
**Não** implementar fuzzy merge nesta fase.

---

## 5. Pacientes históricos importados

| Elemento | Confirmado |
|---|---|
| Banner | «Dados provenientes do registo anterior da clínica. Confirme as informações do utente.» |
| Botão | «Confirmar dados» (`patients.edit`) |
| Depois | «Dados verificados» |
| `migration_id` / provenance | **Preservados** no `metadata` |
| PatientHistory | **Intocado** |
| Quem confirma | Qualquer um com `patients.edit` (Receção incluída) |

Confirmar dados **não** apaga provenance. Correcto.

---

## 6. Campos que a Receção pode actualizar

Via `PATCH` (`patients.edit`): nome, documento, nascimento, género, telefone, email, morada completa, nacionalidade, grupo sanguíneo, estado civil, ocupação; contactos de emergência (nested).

| Tipo | Exemplos |
|---|---|
| CORRECÇÃO ADMINISTRATIVA | telefone, morada, documento, nasc., género, nome, emergência |
| ALTERAÇÃO CLÍNICA (exposta) | grupo sanguíneo; alergias; doenças crónicas; observações **CLINICA** |

Nome é editável **sem** diff old→new no audit (só lista de `changed_fields`).

---

## 7. Nome do paciente

- Receção **pode** alterar nome (`patients.edit`).
- Audit: `PATIENT_UPDATE` com nomes dos campos — **sem** valor anterior/novo.
- **Risco:** mudança de identidade silenciosa vs correcção ortográfica legítima — documentado; sem regra nova nesta auditoria.

---

## 8. Tabs — tabela

| Tab | Receção vê? | Receção edita? | Necessária? | Risco |
|---|---|---|---|---|
| Resumo | SIM | Demografia via Editar | SIM | Timeline pode mostrar eventos clínicos (leitura) |
| «Histórico» (= `/clinical`) | SIM | **SIM** alergias/doenças/observações | Nome confuso; conteúdo clínico | **P0 privacidade / edição** |
| Consultas | SIM (lista **global**) | Não na ficha | PARCIAL | Sem filtro pelo utente; diagnóstico via API appointments |
| Laboratório | **NÃO** (sem permissão) | — | OK oculto | — |
| Pagamentos | SIM (`billing.view`) | Via Faturação | SIM | Deep-link por ID interno |
| Documentos | SIM | Upload/create; delete com edit | PARCIAL | Possíveis anexos clínicos (`file_url`) |

Rota `/patients/:id/history` (timeline completa) existe mas **não** está no SubNav; link desde Resumo.

---

## 9. Resumo

Mostra identidade, contactos, banner importação, `AllergyAlertBanner`, overview, `PatientTimeline` (mistura administrativo + clínico + migrado, com badges).

Adequado para «quem é» + alertas; **não** exige interpretar diagnóstico complexo no Resumo em si, mas a timeline pode expor descrições clínicas migradas/vivas.

---

## 10. Histórico anterior

Timeline e página history usam badges:

- **«Histórico anterior»** (migrado)
- **«SGCS»** (actual)

PatientHistory importado: **só leitura** na UI (sem edição de eventos). Correcto.

---

## 11. Consultas

Tab aponta para `/appointments/list` **sem** `patient id`.  
API `GET /patients/{id}/appointments/` devolve serializer completo incluindo **`diagnosis`**, **`clinical_notes`**.  
Se algum ecrã consumir esse endpoint com permissão view, diagnóstico fica acessível.

**RISCO DE PRIVACIDADE** (API + possível UI futura).

---

## 12. Laboratório

Tab ocultada para Receção típica (sem `laboratory.results.view`).  
Endpoint stub `lab-orders` sob patients.view existe mas vazio.  
**Aceitável** para o piloto se se mantiver oculto.

---

## 13. Pagamentos

Tab → `/billing/history?paciente={id}` (coerente com Faturação / `billing.view`).  
Permite ver resumo financeiro; não cria fatura.  
Ideal: continuar a navegar para faturas existentes no módulo Faturação (já hardened).

---

## 14. Documentos

Lista documentos/fotos; *Abrir* via `file_url`.  
Receção com `patients.edit` pode eliminar; com `create` pode carregar.  
**Risco:** documentos tipo exame externo / clínicos acessíveis ao balcão.

---

## 15. Acção operacional principal

**«Novo atendimento» a partir da ficha: NÃO existe.**

Lacuna P1: fluxo desejado Pacientes → encontrar → iniciar Atendimento rápido **não** está na ficha.  
Atendimento rápido tem a sua própria pesquisa de paciente (duplicação de entrada, não de lógica de check-in).

---

## 16–18. Integrações

| Direcção | Estado |
|---|---|
| Atendimento → Pacientes | SIM (pesquisa / novo com retorno) |
| Pacientes → Atendimento | **NÃO** (falta CTA) |
| Faturação | SIM (tab Pagamentos / billing) |
| Marcações | FRACO (lista global, não por utente) |
| Histórico migrado identificado | SIM (badges + banner confirmar) |

---

## 19. Privacidade e RBAC

| Informação | Classificação |
|---|---|
| Nome / telefone / processo / morada | NECESSÁRIA |
| Alergias (banner Resumo) | ACEITÁVEL (segurança do utente) |
| Editar alergias / crónicas / obs. CLINICA | **DESNECESSÁRIA / RISCO** |
| Diagnóstico / notas clínicas (API consultas) | **RISCO** |
| Prescrições UI | NÃO (stub / sem tab) |
| Resultados lab UI | NÃO (tab oculta) |
| Download documentos | ACEITÁVEL a RISCO (conforme tipo) |
| Delete físico paciente | **NÃO** (só soft; Receção sem `delete`) |

---

## 20. UX

| Problema | Notas |
|---|---|
| «Última visita» = `updated_at` | Enganoso |
| Tab «Histórico» = clínico | Confunde com timeline |
| Datas / idade | Riscos ISO vs DD/MM em vários sítios |
| Consultas/Lab não scoped | Fricção |
| Pagamentos «n.º interno» | ID BD vs PAC-… |

Copy de confirmação importada já em PT institucional — bom.

---

## 21. Inactivo / falecido

- Existe `is_active` / soft-delete.  
- **Não** há estado `deceased` dedicado.  
- Receção **não** desactiva (sem `patients.delete`).  
- Check-in usa queryset activo — inactivo tende a ficar fora do atendimento; documentar sem inventar regras.

---

## 22. Eliminação

| Acção | Receção |
|---|---|
| Soft delete | **NÃO** (sem permissão) |
| Desactivar | **NÃO** |
| Hard delete | **NÃO** na API |

**Não** é RISCO CRÍTICO de delete físico para Receção. Soft delete bloqueado se consultas activas / faturas pendentes (quando quem tem `delete` tenta).

---

## 23. Audit log

| Evento | Auditado? |
|---|---|
| Create / update / confirm | SIM (`PATIENT_*`) |
| Campos alterados | Nomes dos campos — **sem** old/new |
| Nested clínico | Timeline PatientHistory; sem AuditLog PATIENT_* dedicado |

---

## 24. Fluxo real no balcão

| Passo | Funciona? |
|---|---|
| Pesquisar «Nijeoma» | SIM |
| Abrir ficha | SIM |
| Actualizar telefone | SIM |
| Confirmar dados importados | SIM |
| Clicar «Novo atendimento» | **NÃO** |
| Seguir Atendimento → Faturação → fila | SIM **se** entrar pelo Atendimento rápido |

**Fricção:** falta CTA atendimento; tab clínico editável; Consultas não filtradas.  
**Risco:** privacidade clínica + duplicados se aviso ignorado.

---

## 25. Não feito

Sem redesenho, merge, fuzzy, alteração de modelos/migração/RBAC, WhatsApp, portal.

---

## 26. Recomendação e prioridades

**Classificação:** `PRECISA_AJUSTES` + `RISCO_PRIVACIDADE` (+ `QUASE_PRONTO` no núcleo administrativo: pesquisa / registo / confirmar).

| Prioridade | Achado |
|---|---|
| **P0** | Receção edita alergias / doenças / observações clínicas; API consultas expõe diagnóstico/notas |
| **P1** | CTA «Novo atendimento» na ficha → Atendimento rápido com paciente; restringir UI clínica à leitura (ou esconder edição); Consultas filtradas por utente |
| **P2** | Renomear tab «Histórico» clínico; corrigir «Última visita»; datas/idade; grupo sanguíneo fora do form Receção ou só leitura |
| **P3** | Audit log com old/new no nome; scoped Marcações na ficha |

---

## 27. Matriz rápida

| Capacidade | |
|---|---|
| Pesquisa nome / telefone / código | SIM / SIM / SIM |
| Registar novo | SIM |
| Editar administrativos | SIM |
| Confirmar importados | SIM |
| Prevenção duplicados | **PARCIAL** (aviso, sem bloqueio) |
| Novo atendimento na ficha | **NÃO** |
| Delete físico | **NÃO** |

---

**Estado final:** `PATIENTS_AUDIT_COMPLETE`
