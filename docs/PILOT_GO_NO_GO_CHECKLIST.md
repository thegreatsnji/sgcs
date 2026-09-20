# Checklist GO / NO-GO — Piloto SauVida

**Usar depois** do UAT master (`UAT_PILOTO_SAUVIDA_MASTER.md`) e dos UAT por perfil.  
**Não** confundir com `PILOT_READY_FOR_UAT` (pronto para *começar* UAT).

Data: __________ · Ambiente: demo / piloto-real (riscar) · Responsável: __________

---

## GO — todos devem estar SIM

| # | Critério | SIM | NÃO | Evidência |
|---|---|---|---|---|
| G1 | 0 issues **P0** abertas | | | |
| G2 | 0 issues **P1** críticas abertas (bloqueiam trabalho diário) | | | |
| G3 | UAT Receção essencial PASSOU (walk-in + pagamento + assign) | | | |
| G4 | UAT Médico essencial PASSOU (fila exclusiva + SOAP + lab pedido) | | | |
| G5 | UAT Laboratório essencial PASSOU (regularização + validar) | | | |
| G6 | UAT Enfermagem essencial PASSOU (triagem + stock sem negativo) | | | |
| G7 | UAT Director essencial PASSOU (KPIs + sem write operacional) | | | |
| G8 | Impressão necessária (recibo e/ou resultado) validada na impressora real | | | |
| G9 | Suite: `pytest` verde; `check`; `makemigrations --check`; `build` | | | |
| G10 | Backup PostgreSQL **real** (tamanho > 0, checksum, cópia off-server, frequência definida) | | | |
| G11 | HTTPS activo se o piloto expõe dados reais na rede / Internet | | | |
| G12 | `DEBUG=False`, `SECRET_KEY` único, `ALLOWED_HOSTS`/CORS correctos | | | |
| G13 | Contas reais (não `Demo@2026!`); RBAC `seed_rbac` aplicado | | | |
| G14 | Plano de contingência conhecido; contactos preenchidos | | | |
| G15 | Demo vs real: sem `seed_demo` na BD piloto real | | | |

---

## NO-GO — qualquer SIM abaixo impede go-live

| # | Condição | SIM = NO-GO | Notas |
|---|---|---|---|
| N1 | Perda de dados / risco de corrupção sem restauro testado | | |
| N2 | Acesso indevido (clínico, financeiro ou admin) | | |
| N3 | Cálculo financeiro errado (faturado/recebido/saldo/redução) | | |
| N4 | Resultado lab visível a quem não deve / processável sem regularizar | | |
| N5 | Stock negativo possível | | |
| N6 | Backup inexistente ou só stub API (`tamanho_bytes=0`) | | |
| N7 | HTTPS ausente com dados reais expostos | | |
| N8 | Histórico migrado a alterar totais de caixa/faturação | | |

---

## Decisão

| Opção | Condição |
|---|---|
| **GO** | Todos G1–G15 SIM e nenhum N1–N8 |
| **GO CONDICIONADO** | Só P2/P3 abertos; plano de mitigação datado |
| **NO-GO** | Qualquer N* ou P0/P1 aberto |

**Decisão:** GO / GO CONDICIONADO / NO-GO  

**Mitigações (se condicionado):**

1. …
2. …

**Assinatura Director clínico:** __________  
**Assinatura Admin / TI:** __________  
**Data:** __________
