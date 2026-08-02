# Relatório Sprint 15 — Validação dos fluxos reais e planeamento da expansão clínica

**Data:** 2026-07-31  
**Projecto:** SGCS — Sistema de Gestão Clínica SauVida  
**Tipo:** Análise, documentação, modelação, dados e planeamento (**sem** módulos completos Farmácia / Cirurgia / Maternidade)

---

## 1. Objectivos da sprint

| Objectivo | Estado |
|-----------|--------|
| Validar fluxos reais da clínica (pós-visita) | ✅ Documentado em `docs/SPRINT15/FLUXOS_REAIS_VALIDADOS.md` |
| Actualizar requisitos e roadmap por versões | ✅ `ROADMAP_MODULOS_POR_VERSAO.md` + `SRS/PRODUCT_ROADMAP.md` |
| Catálogo real de serviços e preços (estrutura + import) | ✅ CSV + `import_servico_catalog` |
| Dados iniciais da clínica | ✅ JSON + `seed_clinic_initial` |
| Diagramas e documentação | ✅ `DIAGRAMAS_FLUXOS.md` |
| Identificar lacunas do sistema actual | ✅ `LACUNAS_E_PRIORIDADES.md` |
| Definir próximos módulos sem desenvolvimento prematuro | ✅ v1.4–v1.9 especificados; v1.6–v1.8 bloqueados |

---

## 2. Entregáveis

### Documentação

| Artefacto | Caminho |
|-----------|---------|
| Índice Sprint 15 | `docs/SPRINT15/README.md` |
| Fluxos validados | `docs/SPRINT15/FLUXOS_REAIS_VALIDADOS.md` |
| Lacunas e prioridades | `docs/SPRINT15/LACUNAS_E_PRIORIDADES.md` |
| Roadmap por versão | `docs/SPRINT15/ROADMAP_MODULOS_POR_VERSAO.md` |
| Catálogo e preços | `docs/SPRINT15/CATALOGO_SERVICOS_PRECOS.md` |
| Diagramas | `docs/SPRINT15/DIAGRAMAS_FLUXOS.md` |
| Dados iniciais | `docs/SPRINT15/DADOS_INICIAIS_CLINICA.md` |
| Guia entrevistas (referência) | `docs/ENTREVISTAS_FLUXOS_CLINICA.md` |

### Dados e configuração

| Artefacto | Caminho |
|-----------|---------|
| Perfil clínica (template) | `data/clinic/perfil_clinica.json` |
| Departamentos | `data/clinic/departamentos_sauvida.json` |
| Catálogo serviços | `data/clinic/catalogo_servicos_sauvida.csv` |

### Comandos Django (sem novos apps)

| Comando | Função |
|---------|--------|
| `import_servico_catalog` | Importa/actualiza `Servico` a partir de CSV |
| `seed_clinic_initial` | Carrega perfil + departamentos; opcional `--import-catalog` |

---

## 3. O que **não** foi feito (conforme âmbito)

- Apps ou UI de **Farmácia**, **Cirurgia**, **Maternidade/Parteira**, **Internamento** completos  
- Alterações ao modelo de dados além do uso de `Servico` / `Departamento` / `PerfilClinica` existentes  
- Preços finais em produção (dependem de revisão da direcção sobre o CSV)

---

## 4. Próximos passos recomendados

1. **Clínica:** Preencher NIF/morada/logótipo e substituir preços no CSV pelos preçários oficiais.  
2. **Operação:** `seed_clinic_initial --import-catalog` no ambiente piloto.  
3. **UAT:** Checklist sec. 6 de `ENTREVISTAS_FLUXOS_CLINICA.md`.  
4. **Sprint 1.3.1 (código):** Cancelamento UI, impressões, forgot password, notificação lab.  
5. **SRS v1.4:** Enfermagem + triagem antes de qualquer sprint de implementação.

---

## 5. Critérios de aceitação Sprint 15

| Critério | Cumprido |
|----------|:--------:|
| Fluxos reais documentados vs. SGCS | ✓ |
| Novos departamentos mapeados sem código prematuro | ✓ |
| Catálogo importável alinhado a `billing.Servico` | ✓ |
| Lacunas e prioridades P0–P3 | ✓ |
| Roadmap reorganizado por versão | ✓ |
| Comandos de importação documentados | ✓ |

---

*Sprint 15 concluída do ponto de vista de análise e documentação. Aguarda validação da direcção clínica sobre preçário e regras RN-01 a RN-06.*
