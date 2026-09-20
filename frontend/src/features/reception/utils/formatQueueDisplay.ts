/** Formatação de apresentação da fila (sem alterar cálculos). */

/** Ex.: 1 → "1.º na fila" */
export function formatQueuePosition(position: number): string {
  if (!Number.isFinite(position) || position < 1) return String(position);
  return `${Math.trunc(position)}.º na fila`;
}

/**
 * Tempo estimado aproximado, em Português institucional.
 * Não altera o valor em minutos — só a apresentação.
 */
export function formatEstimatedWaitMinutes(minutes: number): string {
  const m = Math.max(0, Math.round(minutes));
  if (m < 60) {
    return `cerca de ${m} min`;
  }
  const hours = Math.floor(m / 60);
  const rem = m % 60;
  if (rem === 0) {
    return hours === 1 ? "cerca de 1 h" : `cerca de ${hours} h`;
  }
  if (hours === 1) {
    return `cerca de 1 h ${rem} min`;
  }
  return `cerca de ${hours} h ${rem} min`;
}

export function formatEstimatedWaitLabel(minutes: number | null | undefined): string {
  if (minutes == null) return "sem estimativa";
  return formatEstimatedWaitMinutes(minutes);
}
