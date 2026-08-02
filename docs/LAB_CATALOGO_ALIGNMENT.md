# Alinhamento laboratório ↔ catálogo de serviços

O **Serviço** (`billing.Servico`) é a fonte oficial do preço. Campos legados nos tipos de exame mantêm-se nesta sprint.

| Exame | Serviço associado | Preço do exame | Preço do serviço | Situação | Acção |
|---|---|---:|---:|---|---|
| Hemograma Completo (LAB-HEMO-TIPO) | LAB-HEMO | — | REVISAR_COM_CLINICA | NECESSITA REVISÃO | Confirmar preço do serviço na clínica |
| Glicemia (LAB-GLIC-TIPO) | LAB-GLIC | — | REVISAR_COM_CLINICA | NECESSITA REVISÃO | Confirmar preço do serviço na clínica |
| Ureia (LAB-UREIA-TIPO) | LAB-UREIA | — | REVISAR_COM_CLINICA | NECESSITA REVISÃO | Confirmar preço do serviço na clínica |
| Creatinina (LAB-CREAT-TIPO) | LAB-CREAT | — | REVISAR_COM_CLINICA | NECESSITA REVISÃO | Confirmar preço do serviço na clínica |
| Exame de Urina (LAB-URINA-TIPO) | LAB-URINA | — | REVISAR_COM_CLINICA | NECESSITA REVISÃO | Confirmar preço do serviço na clínica |
| Exame de Fezes (LAB-FEZES-TIPO) | LAB-FEZES | — | REVISAR_COM_CLINICA | NECESSITA REVISÃO | Confirmar preço do serviço na clínica |
| β-HCG (LAB-HCG-TIPO) | LAB-HCG | — | REVISAR_COM_CLINICA | NECESSITA REVISÃO | Confirmar preço do serviço na clínica |
| Teste VIH (LAB-VIH-TIPO) | LAB-VIH | — | REVISAR_COM_CLINICA | NECESSITA REVISÃO | Confirmar preço do serviço na clínica |
| HBsAg (LAB-HBS-TIPO) | LAB-HBS | — | REVISAR_COM_CLINICA | NECESSITA REVISÃO | Confirmar preço do serviço na clínica |

**Estratégia de transição:** novos pedidos laboratoriais devem usar `TipoExameLaboratorio.servico` quando definido; preços antigos em faturas não são recalculados.