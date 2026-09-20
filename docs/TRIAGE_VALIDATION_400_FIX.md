# Triagem — correcção UAT 400 (validação de sinais vitais)

## Reprodução

Endpoint: `POST /api/v1/reception/check-in/`

Payload observado (vitais):

| Campo | Valor |
|-------|-------|
| TA | 110/50 |
| Temperatura | 35 °C |
| SpO₂ | 12 % |
| FC | 65 |
| FR | 80 |

## Causa raiz

**Os vitais UAT são válidos no domínio técnico do backend** (`CheckInCreateSerializer`).
A validação do serializer aceita este payload (testado).

O sintoma «Request failed with status code 400» tinha duas camadas:

1. **UX / parsing de erros** — respostas DRF no formato `{ "campo": ["…"] }` ou `{ "detail": "…" }` **não** eram interpretadas por `getApiErrorMessage`, que só lia o envelope `message` / `errors`. O Axios caía na mensagem técnica em inglês.
2. **400 de negócio frequente em UAT** — segundo check-in do mesmo utente: *«O paciente já se encontra na fila de espera.»* (também aparecia como Axios 400 sem texto PT).

Não houve rejeição dos valores 110/50, 35, 12, 65 ou 80 por limites clínicos.

## Matriz FE / BE (domínio técnico)

| Campo | FE aceita | FE avisa | BE aceita | BE rejeita | Motivo |
|-------|-----------|----------|-----------|------------|--------|
| TA sistólica/diastólica | formato `NNN/NNN` | fora 90–140 / 60–90 | texto com regex 120/80 | formato inválido | domínio + aviso clínico |
| Temperatura | 30–43 | &lt;35 ou fora 36.1–37.5 | 30–43 | fora do intervalo | alinhado |
| SpO₂ | 0–100 | &lt;95 | 0–100 | fora do intervalo | alinhado (12% é aviso, não bloqueio) |
| FC | 20–250 | fora 60–100 | 20–250 | fora do intervalo | alinhado |
| FR | 5–80 | fora 12–20 | 5–80 | fora do intervalo | alinhado (80 no limite) |
| Peso | &gt;0 | — | obrigatório com triagem | em falta | — |
| Altura | 30–250 opcional | — | 30–250 opcional | fora do intervalo | alinhado |

## Comportamento final

- **Inválido (domínio):** bloqueia no FE (Zod) e/ou BE; mensagem PT no campo; formulário **não** é limpo.
- **Invulgar (clínico):** aviso + modal «Existem valores fora do habitual…» → «Voltar e verificar» / «Confirmar e concluir triagem».
- Confirmação registada em auditoria: `metadata.unusual_vitals_confirmed`.
- Valores **nunca** são clampados nem «corrigidos».
- Toast nunca mostra «Request failed with status code 400».

## Testes

`apps/reception/tests/test_triage_uat_vitals.py`:

- vitais UAT persistidos exactamente;
- vitais normais OK;
- duplicado na fila → 400 PT;
- SpO₂/FR fora do domínio → 400 no campo;
- ENFERMEIRO pode concluir triagem com vitais invulgares.

## RBAC

Sem alterações de perímetro: `reception.create` para RECECIONISTA e ENFERMEIRO (Sprint 26).
