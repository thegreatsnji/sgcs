# Relatório Sprint 17 — Validação de preços e consolidação do catálogo

## 1. Resumo executivo

A Sprint 17 consolidou o processo de **validação presencial de preços** sem importar valores inventados ou marcados `REVISAR_COM_CLINICA`. Foram entregues auditoria dos 36 serviços, ficheiro CSV para a clínica, documentação de importação, regras de faturação com preço confirmado, interface administrativa de serviços e médicos, alinhamento laboratorial documentado, melhorias no `ServiceSearchPicker`, pacote de validação presencial e testes automatizados.

**Regra cumprida:** nenhum preço pendente foi importado como confirmado; `precos_validacao_clinica.csv` mantém `preco_confirmado_fcfa` vazio até à sessão com a clínica.

## 2. Auditoria dos 36 serviços

Ver `docs/SPRINT17_DATA_AUDIT.md`: **36 auditados**, **0 CONFIRMADO**, **36 PENDENTE** (preço de referência `REVISAR_COM_CLINICA` ou vazio).

## 3–7. Preços

| Métrica | Valor |
|--------|------:|
| Serviços confirmados (BD) | 0 (aguardam CSV validado) |
| Preços importados nesta sprint | 0 |
| Preços ignorados / pendentes | 36 no CSV de validação |
| Histórico de preço | Activo (`ServicoPrecoHistorico`, origem `IMPORTACAO_VALIDADA`) |

## 8. Interface administrativa de serviços

- Lista com pesquisa, filtros (categoria, departamento, especialidade, estado, validação, sem preço confirmado), ordenação e paginação.
- Detalhe com histórico de preços (`GET .../price-history/`).
- Criar / editar (preço só Administrador).
- Exportação CSV da página actual.

## 9. Configuração de médicos

- API `GET/PATCH /api/v1/settings/medico-perfis/`.
- UI `settings/medicos` — lista, horário, serviço de consulta (preço via `Servico`).

## 10. Alinhamento laboratório

- `docs/LAB_CATALOGO_ALIGNMENT.md` (9 exames vs catálogo).
- Comando `align_lab_services` (`--dry-run` / `--apply`).

## 11. Receção

- `operacional=1` exige `preco_confirmado=True`.
- `assert_servico_faturavel` com mensagem PT: *"O preço deste serviço ainda não foi confirmado pela clínica. Contacte o Administrador."*
- Administrador pode faturar pendente (regra existente em `servico_pode_faturar`).

## 12. Pacote de validação

- `docs/PACOTE_VALIDACAO_CLINICA_SPRINT17.md`
- `docs/FICHA_VALIDACAO_PRECOS_CLINICA.md` (impressão)

## 13. Permissões

Confirmadas em código e testes (`test_sprint17.TestPermissoesPreco`): Director e Rececionista não alteram preço via API; Administrador sim.

## 14. Migrations

- `billing.0003_sprint17_preco_confirmado` — `preco_confirmado`, `preco_confirmado_em`, `preco_confirmado_por`, `permite_faturacao_sem_preco_confirmado`.

## 15. Endpoints relevantes

- Filtros serviços: `estado_validacao`, `sem_preco_confirmado`, `pendente_validacao`, `ordering=departamento`.
- `settings/medico-perfis/`

## 16. Ficheiros principais

- `backend/apps/billing/models.py`, `catalog_service.py`, `filters.py`, `import_catalogo_sauvida.py`
- `backend/apps/settings/views.py` — `MedicoPerfilViewSet`
- `backend/data/precos_validacao_clinica.csv`
- `frontend/.../ServicesListPage`, `ServiceDetailPage`, `ServiceFormPage`, `ServiceSearchPicker`, `MedicoProfilesPage`
- Documentação Sprint 17 em `docs/`

## 17. Testes

- **279** testes pytest aprovados (incl. 8 em `test_sprint17.py`).

## 18. Build

- `npm run build` — **OK**.

## 19. Lint

- `npm run lint` — **0 erros** (avisos pré-existentes).

## 20. Problemas conhecidos

- Imagem Docker backend local pode carecer de rebuild para incluir `openpyxl` (presente em `requirements/base.txt`).
- Médicos novos exigem criação de `MedicoPerfil` após utilizador MEDICO existir (sem wizard de criação de utilizador nesta página).
- Catálogo de 36 serviços ainda não materializado na BD até `import_catalogo_sauvida --apply --materialize-without-price` (opcional antes da validação de preços).

## 21. Decisões pendentes

- Confirmação presencial de todos os preços FCFA.
- Autorizações temporárias `permite_faturacao_sem_preco_confirmado` caso a clínica queira faturar antes de fechar o CSV completo.

## 22. Recomendação Sprint 18

1. Sessão presencial com `precos_validacao_clinica.csv` preenchido → `--dry-run` → `--apply`.
2. Materializar serviços + `align_lab_services --apply`.
3. Configurar `MedicoPerfil` para médicos activos.
4. Piloto de faturação real na receção com checklist do pacote.
5. Iniciar módulos clínicos acordados (ecografia/cirurgia/maternidade) só após preços confirmados.
