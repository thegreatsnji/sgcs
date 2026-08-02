# Perfis não operacionais — Clínica SauVida

**Perfis operacionais confirmados:** `ADMINISTRADOR`, `DIRECTOR`, `MEDICO`, `RECECIONISTA`, `LABORATORIO`.

## Perfis extra no código (mantidos por compatibilidade)

| Perfil | Definição principal | Utilizadores demo | UI criação utilizadores |
|--------|---------------------|-------------------|-------------------------|
| `ENFERMEIRO` | `apps/authentication/models.py` (`UserRole`) | **Não** criado por `seed_demo` | **Não** em `ASSIGNABLE_ROLES` (`frontend/src/constants/roles.ts`) |
| `FINANCEIRO` | Idem + `seed_rbac.py` (`DEFAULT_ROLE_PERMISSIONS`) | **Não** criado por `seed_demo` | **Não** em `ASSIGNABLE_ROLES` |

### Onde aparecem

- **Backend:** `UserRole` choices, `seed_rbac.py` (permissões `FINANCEIRO` e `ENFERMEIRO` preservadas), testes unitários pontuais (ex.: `test_patients.py`, `test_clinical_record.py`) que instanciam `ENFERMEIRO` manualmente.
- **Frontend:** tipos em `user.ts`, etiquetas em `AppHeader.tsx`, rota por defeito em `roleRouting.ts` para `FINANCEIRO` / `ENFERMEIRO` — apenas se um utilizador legado existir na BD.
- **Grupos RBAC:** o grupo predefinido «Financeiro» foi **removido** de `DEFAULT_GROUPS` em `seed_rbac` para não sugerir equipa operacional.

### Política SauVida (esta fase)

- Não criar utilizadores `ENFERMEIRO`, `FINANCEIRO` nem perfil **Caixa** em produção/demo.
- Triagem clínica básica permanece na **Receção** (`TriageCheckInWizard`, `apps/reception`).
- Expansão futura (módulo Enfermagem dedicado) pode reactivar `ENFERMEIRO` sem alterar o enum.

### Verificação

- `seed_demo`: apenas 6 utilizadores nos perfis operacionais (`DEMO_USERS` em `seed_demo.py`).
- Testes: `test_sprint15_reception_billing.py::TestSeedDemoProfiles`.
