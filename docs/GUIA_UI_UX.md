# Guia UI/UX — SGCS SauVida

## Princípios

1. **Português** em toda a interface.
2. **Menos cliques** — fluxos por perfil (recepção, médico, lab., director).
3. **Feedback claro** — skeleton, empty states, toasts.
4. **Responsivo** — mobile, tablet, desktop (grids `sm:` / `lg:` / `xl:`).
5. **Acessibilidade** — `focus-ring`, `aria-label`, contraste em badges.

## Design system

- Cartões `rounded-2xl`, bordas suaves, modo escuro via `ThemeContext`.
- Tipografia: títulos `text-2xl`/`text-3xl`, corpo `text-sm`.
- Moeda: componente `CurrencyDisplay` (FCFA).

## Performance

- React Query com `refetchInterval` onde faz sentido (fila, painéis).
- Pesquisa com **debounce** (`useDebouncedValue`, 250 ms).
- Listas longas: paginação API; virtualização quando necessário (futuro).

## Impressão

Use `PrintDocumentFrame` para cabeçalho, data, operador e rodapé consistentes.
