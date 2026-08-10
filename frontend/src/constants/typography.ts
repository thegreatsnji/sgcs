/**
 * Hierarquia tipográfica SGCS — usar Inter (font-sans) em todo o produto.
 * Não definir tamanhos/pesos ad hoc em páginas individuais.
 */
export const TYPO = {
  pageTitle: "text-2xl font-semibold tracking-tight text-text sm:text-[1.625rem]",
  sectionTitle: "text-lg font-semibold text-text",
  cardTitle: "text-base font-semibold text-text",
  body: "text-sm text-text",
  bodyMuted: "text-sm text-text-muted",
  label: "text-sm font-medium text-text",
  meta: "text-xs text-text-muted",
  eyebrow: "text-xs font-medium text-text-muted",
} as const;
