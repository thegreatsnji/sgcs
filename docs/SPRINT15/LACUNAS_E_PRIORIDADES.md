# Lacunas do sistema actual e prioridades

**Sprint 15** — complementa [AUDITORIA_PRE_SPRINT14.md](../AUDITORIA_PRE_SPRINT14.md)

---

## 1. Lacunas funcionais (já implementado vs. clínica)

| Prioridade | Lacuna | Impacto | Acção recomendada | Versão |
|:----------:|--------|---------|-------------------|--------|
| P0 | Preçário real não carregado em produção | Faturação incorrecta | Importar `data/clinic/catalogo_servicos_sauvida.csv` e validar valores com director | **15 / go-live** |
| P0 | Dados institucionais incompletos (NIF, morada, logótipo) | Documentos legais | Preencher `perfil_clinica.json` + UI settings | **15** |
| P1 | Cancelamento consulta sem botão na UI | Operação diária | Ligar API existente | **1.3.1** |
| P1 | Impressões não ligadas a todos os ecrãs | Papel ainda manual | Ligar wrappers Sprint 14 | **1.3.1** |
| P1 | Recuperação de palavra-passe | Suporte TI | Fluxo forgot/reset | **1.3.1** |
| P2 | Seguro do paciente sem UI | Poucos casos? | UI se RN confirmar uso | **1.3.2** |
| P2 | CID-10 texto livre | Codificação | Catálogo pesquisável | **1.4** |
| P2 | Notificação lab→médico (Celery stub) | Atraso clínico | Canal definido em RN-03 | **1.3.1** |
| P3 | Role ENFERMEIRO sem jornada | Novo departamento | Módulo enfermagem | **1.4** |
| P3 | Pedido imagiologia sem fila/sala | Ecografia | Módulo imagiologia | **1.5** |
| — | Farmácia / stock | Dispensação | **Não iniciar** até v1.6 | **1.6** |
| — | Cirurgia / bloco | OT | **Não iniciar** até v1.7 | **1.7** |
| — | Maternidade / parteira / parto | GO completo | **Não iniciar** até v1.8 | **1.8** |
| — | Gestão de camas | Internamento | **Não iniciar** até v1.9 | **1.9** |

---

## 2. Lacunas de catálogo e faturação

| Tema | Situação | Sprint 15 |
|------|----------|-----------|
| Categorias `Servico` | CONSULTA, EXAME, PROCEDIMENTO, INTERNAMENTO, OUTRO | Suficiente para catálogo inicial; medicamentos como OUTRO até farmácia |
| Preços ecografia / cirurgia / parto | No CSV de referência | **Substituir** pelos preçários recolhidos na visita |
| Pacotes (kit parto, cirurgia) | Linhas OUTRO/PROCEDIMENTO | Validar com director se fatura itemizado ou pacote |
| Descontos / seguros | Não modelado | Fase 2 — após decisão RN seguros |

---

## 3. Lacunas organizacionais (não são bugs)

| Departamento na clínica | Registo SGCS Sprint 15 |
|-------------------------|-------------------------|
| Enfermagem, Triagem, Farmácia, etc. | `departamentos_sauvida.json` (config) |
| Módulos de software | Roadmap v1.4–v1.9 apenas documentado |

---

## 4. Priorização para desenvolvimento (pós-Sprint 15)

1. **Go-live núcleo:** F1–F11 + catálogo + perfil clínica + impressões + cancelamento UI.  
2. **v1.4:** Enfermagem + triagem (workflow único).  
3. **v1.5:** Imagiologia/ecografia + extensão lab/imunologia.  
4. **v1.6–v1.9:** Farmácia, cirurgia, maternidade, internamento — **só após** SRS por módulo aprovado pela direcção.

---

## 5. Riscos se avançar sem validação

| Risco | Mitigação Sprint 15 |
|-------|---------------------|
| Construir farmácia antes de regras de stock/preço | Proibido nesta sprint; apenas catálogo `Servico` |
| Preços demo em produção | Comando import + revisão director |
| Fluxos paralelos no papel | FLUXOS_REAIS_VALIDADOS.md como contrato |

---

*Actualizar quando itens P0/P1 forem fechados.*
