# Tempos-alvo e medição — UAT SauVida

**Sprint 20** — registar na sessão presencial; desvios &gt; 50% da meta devem ser analisados.

## Metas iniciais

| Actividade | Meta | Notas |
|------------|-----:|-------|
| Pesquisa de paciente | **≤ 2 s** | Após 2 caracteres; rede piloto estável |
| Pesquisa de serviço (fatura) | **≤ 2 s** | Catálogo operacional em memória/cache |
| Criação de paciente | medir | Depende de campos obrigatórios |
| Criação de fatura (1 serviço) | medir | Inclui selecção paciente |
| Pagamento + confirmação | medir | |
| Emissão de recibo (até impressão) | **≤ 30 s** | Inclui diálogo impressora |
| Check-in + triagem | medir | |
| Abertura consulta / PCE | **≤ 3 s** | Time-to-interactive percepção |
| Registo resultado lab. (caso simples) | medir | |
| **Atendimento simples recepção** (pesquisa → fatura → pago → recibo) | **≤ 2 min** | 1 serviço, pagamento integral |

## Folha de registo (por tentativa)

| # | Operador | Data/hora | Fluxo | Meta (s) | Medido (s) | Desvio % | Rede | Dispositivo | Observações |
|---|----------|-----------|-------|----------:|----------:|---------:|------|-------------|-------------|
| 1 | | | Pesquisa paciente | 2 | | | | | |
| 2 | | | Pesquisa serviço | 2 | | | | | |
| 3 | | | Atendimento simples | 120 | | | | | |
| 4 | | | Recibo | 30 | | | | | |
| 5 | | | Abrir consulta | 3 | | | | | |

## Desvios conhecidos (pré-UAT técnico)

| Item | Situação | Acção |
|------|----------|-------|
| Primeira carga SPA | Pode exceder 3 s em 3G | Cache assets; HTTPS + CDN opcional |
| Impressora USB/rede | Fora do SGCS | Testar driver na sessão R17 |
| BD remota | Latência VPS | Medir no mesmo host que produção piloto |

Consolidar resultados em [SPRINT20_UAT_REPORT.md](SPRINT20_UAT_REPORT.md).
