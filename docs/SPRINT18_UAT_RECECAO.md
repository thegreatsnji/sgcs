# Sprint 18 — UAT Receção

Ambiente: demonstração / dados fictícios. Evidência principal: testes automatizados (`test_sprint15_reception_billing`, `test_sprint17`, `test_sprint18`).

| Caso | Resultado esperado | Resultado obtido | Estado | Evidência | Correcção |
|---|---|---|---|---|---|
| Pesquisar paciente | Lista com filtro | API `patients` com permissão | APROVADO | `PatientsListPage`, testes pacientes | — |
| Nova fatura | Formulário com serviços operacionais | `operacional=1` + preço confirmado | APROVADO | `InvoiceCreatePage` | — |
| Serviço sem preço confirmado | Bloqueio com mensagem PT | `MSG_PRECO_NAO_CONFIRMADO` | APROVADO | `test_sprint17` | — |
| Pagamento total / parcial | Estados PARCIAL/PAGA | `BillingService` | APROVADO | `test_billing` | — |
| Recibo e impressão | Dados da clínica no recibo | Página recibo | NECESSITA AJUSTE | Validar em piloto físico | Checklist impressão S18 |
| Alterar preço na receção | 400 / recusado | Serializer RBAC | APROVADO | `test_sprint17` permissões | — |
| Importar catálogo | Sem permissão | Sem rota receção | APROVADO | RBAC seed | — |
| Configurar médicos | Sem permissão | settings restrito | APROVADO | RBAC | — |

**Nota:** fluxos 4–7 (marcação, check-in, triagem) dependem de dados demo; repetir na sessão presencial com `PACOTE_VALIDACAO_CLINICA_SPRINT17.md`.
