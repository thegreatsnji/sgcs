# Guia de testes de utilizador — SGCS SauVida

## Preparação

```bash
npm run start
```

Abrir http://localhost:5173 — credenciais em [DEMO_DATA.md](./DEMO_DATA.md).

Guia completo: [DEV_RUNBOOK.md](./DEV_RUNBOOK.md).

## Matriz mínima por perfil

| Cenário | Admin | Director | Médico | Receção | Lab | Enfermagem |
|---------|:-----:|:--------:|:------:|:-------:|:---:|:----------:|
| Login e landing correcto | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Menu adequado (sem itens proibidos) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Dashboard do perfil carrega | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Pesquisa de paciente | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| Check-in / fila | — | — | — | ✓ | — | — |
| Abrir consulta / PCE | — | — | ✓ | — | — | ver |
| Pedido / resultado lab | — | — | ver | — | ✓ | — |
| Fatura / pagamento (FCFA) | ✓ | ✓ | ✗ | parcial* | ✗ | ✗ |
| Relatórios / executivo | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Configurações / backups | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |

\*Pagamentos básicos na receção apenas se o RBAC o permitir.

## Responsividade

Validar em:

- Desktop (≥ 1280px)
- Tablet (~768–1024px) — prioridade médico e receção
- Telemóvel (~375px)

## Impressão

Em cada documento (paciente, receita, lab, fatura, recibo): verificar logótipo/nome, data, número, rodapé e legibilidade em pré-visualização de impressão.

## Critérios de falha

- Texto em inglês na UI
- Acesso a módulo não permitido pelo perfil
- Build ou lint com erros críticos
- Valores monetários sem indicação FCFA
- Crash ao abrir o dashboard do perfil
