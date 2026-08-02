# Fluxo — preço flexível na receção

1. Seleccionar serviço operacional com preço confirmado.
2. Sistema preenche preço oficial (`servico.preco`).
3. Por defeito, preço cobrado = preço oficial (`origem_preco=CATALOGO`).
4. Rececionista activa **«Aplicar redução do valor»**.
5. Introduz valor cobrado (0 ≤ valor ≤ oficial).
6. Sistema calcula diferença e percentagem.
7. Selecciona motivo; se «Outro», observação obrigatória.
8. Se percentual ≤ limite configurado (ou limite vazio): `APROVADA_AUTOMATICAMENTE`.
9. Se acima do limite: criar pedido em `/api/v1/billing/reducoes/` e aguardar aprovação Director/Administrador.
10. Fatura só inclui linha com `autorizacao_reducao_id` aprovada quando acima do limite.
11. Registo em auditoria (`REDUCAO_VALOR_APLICADA`).

Mensagens UI (PT): ver especificação Sprint 18.1.
