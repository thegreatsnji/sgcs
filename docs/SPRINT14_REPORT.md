# Relatório Sprint 14 — UI/UX Premium e Refinamento de Fluxos

**Data:** 2026-07-16  
**Projecto:** SGCS — Sistema de Gestão Clínica SauVida  
**Pré-requisito:** [AUDITORIA_PRE_SPRINT14.md](./AUDITORIA_PRE_SPRINT14.md)

---

## 1. Resultado da auditoria prévia

| Métrica | Valor |
|--------|------:|
| Funcionalidades verificadas | 168 |
| CONCLUÍDO | 142 |
| PARCIAL | 24 |
| AUSENTE (antes da Sprint 14) | 2 (forgot-password; seed_demo) |
| Críticos | 3 — todos corrigidos antes do arranque |

Decisão automática: **iniciar Sprint 14** após correcção dos críticos.

---

## 2. Problemas encontrados e corrigidos (pré-Sprint + Sprint)

| ID | Problema | Resolução |
|----|----------|-----------|
| C1 | Refresh JWT sem persistir novo `refresh` | `frontend/src/services/api/client.ts` |
| C2 | Receção podia editar PCE via fallback `appointments.edit` | `backend/apps/appointments/permissions.py` |
| C3 | Teste médico × dashboard receção desactualizado | `test_reception.py` → 403 |
| S14 | `seed_demo` ausente | `apps/users/management/commands/seed_demo.py` |

---

## 3. Entregas Sprint 14

### Comando `seed_demo`

- 1 Admin, 1 Director, 2 Médicos, 1 Rececionista, 1 Lab
- Pacientes, consultas, fila, lab, fatura/pagamento, notificações
- **Sem** utilizador FINANCEIRO
- Credenciais impressas no terminal (`Demo@2026!`)

### Frontend

- `CurrencyDisplay` + `utils/currency.ts` (FCFA)
- Layouts de impressão (`components/print/*` + `styles/print.css`)
- Re-exports seguros design-system ↔ `components/ui`
- Copy PT (`uiCopy.ts`, `navigation.ts`)
- Painéis por perfil já existentes validados (Admin, Director, Médico, Receção, Lab)

### Documentação

| Documento | Estado |
|-----------|--------|
| `docs/AUDITORIA_PRE_SPRINT14.md` | Criado |
| `docs/DEMO_DATA.md` | Criado |
| `docs/UI_UX_GUIDE.md` | Criado |
| `docs/ROLE_DASHBOARDS.md` | Criado |
| `docs/USER_TESTING_GUIDE.md` | Criado |
| `docs/SPRINT14_REPORT.md` | Este ficheiro |
| README, Arquitetura, Roadmap, SystemAdministration, Deployment | Actualizados |

---

## 4. Testes e qualidade

| Verificação | Resultado |
|-------------|-----------|
| `pytest` (Docker) | **245 passed** |
| `npm run build` | **OK** |
| Lint frontend | **0 errors**, 7 warnings (react-refresh / hooks) |
| JWT / contratos API | **Inalterados** |

---

## 5. Credenciais demo geradas

| Perfil | E-mail | Palavra-passe |
|--------|--------|---------------|
| Administrador | admin@sauvida.gw | Demo@2026! |
| Director | director@sauvida.gw | Demo@2026! |
| Médico | medico1@sauvida.gw | Demo@2026! |
| Médico | medico2@sauvida.gw | Demo@2026! |
| Receção | rececao@sauvida.gw | Demo@2026! |
| Laboratório | laboratorio@sauvida.gw | Demo@2026! |

---

## 6. Pontos para validação da proprietária

1. Branding final (logótipo oficial, cores institucionais)
2. Textos legais em faturas/recibos impressos (NIF, morada)
3. Fluxo de cancelamento de consulta na UI (API já existe)
4. UI de seguros do paciente
5. Recuperação de palavra-passe (forgot/reset) — fora do âmbito UI-only se exigir backend
6. Ligação dos wrappers de impressão a cada ecrã de detalhe
7. Confirmação visual tablet (médico + receção) em dispositivo real

---

## 7. Critérios de aceitação

| Critério | Estado |
|----------|--------|
| Auditoria documentada | ✓ |
| Sem problemas críticos | ✓ |
| Testes existentes verdes | ✓ |
| Frontend compila | ✓ |
| Painel próprio por perfil | ✓ |
| Menu por perfil | ✓ |
| Interface em Português | ✓ (limpeza contínua) |
| `seed_demo` com 6 utilizadores | ✓ |
| Sem utilizador FINANCEIRO | ✓ |
| JWT/API inalterados | ✓ |
