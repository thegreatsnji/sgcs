# Decisão: faturação na Receção vs módulo Finance

**Data:** 2026-07-31  
**Contexto:** Clínica SauVida — toda a faturação, pagamentos e recibos na Receção.

## Fluxo operacional (`apps/billing`)

O módulo **billing** é o canal **operacional** diário:

1. Seleccionar paciente e serviços (`Servico`, preço em FCFA).
2. Criar fatura (`Fatura`) e, se necessário, orçamento prévio.
3. Registar pagamento total ou parcial (`Pagamento`) e confirmar.
4. Emitir e consultar recibo (`Recibo`), imprimir (`billing.print`).
5. Consultar histórico financeiro do paciente (`patient-history`).

A Receção (`RECECIONISTA`) possui permissões: `billing.view`, `billing.create`, `billing.edit`, `billing.payment`, `billing.receipt`, `billing.print` — **sem** `billing.delete`, `billing.export` nem módulo `finance.*`.

## Módulo administrativo / legado (`apps/finance`)

O módulo **finance** (caixas, movimentos, despesas, dashboard financeiro separado) **permanece no código** para compatibilidade e uso administrativo futuro, mas **não** faz parte do fluxo diário da Receção SauVida:

- Menu **Financeiro** e **Caixa** não são mostrados à Receção.
- Pagamentos operacionais devem ser registados apenas em **billing**; relatórios de receita alimentam-se dos mesmos modelos (`Pagamento`, `Fatura`, `Recibo`).

## Responsabilidades

| Perfil | Faturação operacional | Relatórios / indicadores | Config. financeira | Caixa / despesas |
|--------|----------------------|---------------------------|--------------------|------------------|
| **RECECIONISTA** | Sim (billing) | Não | Não | Não |
| **DIRECTOR** | Consulta + relatórios | Sim (`reports.*`, finance.view) | Não (settings avançados) | Sim (finance) |
| **ADMINISTRADOR** | Total | Total | Total | Total |

## Riscos de duplicação

- Registar o **mesmo** pagamento em `billing` e em movimentos de **caixa** (`finance`) pode duplicar valores nos relatórios se ambos forem usados em paralelo.
- **Mitigação actual:** Receção sem `finance.view`; documentação e formação para usar apenas billing na recepção física.
- **Recomendação futura:** consolidar reporting numa única fonte (billing) ou sincronização explícita finance ← billing, com feature flag desactivada em SauVida até decisão da direcção.

## Recomendação

Manter **billing** como único fluxo na Receção; reservar **finance** a revisão administrativa pelo Director/Administrador, sem criar perfil **Caixa** ou **Financeiro** operacional nesta fase.
