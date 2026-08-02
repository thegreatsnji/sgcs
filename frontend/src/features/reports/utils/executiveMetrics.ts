export function formatCompactCurrency(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M FCFA`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}k FCFA`;
  return `${value.toLocaleString("pt-PT")} FCFA`;
}

export function formatChartDate(iso: string): string {
  const [, month, day] = iso.split("-");
  return `${day}/${month}`;
}

export function computeSeriesTrend(series: Array<{ data: string; valor: number }>) {
  if (series.length < 2) {
    return { delta: 0, label: "Sem histórico", positive: true };
  }
  const last = series[series.length - 1]?.valor ?? 0;
  const prev = series[series.length - 2]?.valor ?? 0;
  if (prev === 0) {
    const positive = last >= 0;
    return { delta: last > 0 ? 100 : 0, label: last > 0 ? "Novo pico" : "Estável", positive };
  }
  const delta = ((last - prev) / prev) * 100;
  const positive = delta >= 0;
  return {
    delta,
    label: `${positive ? "+" : ""}${delta.toFixed(1)}% vs. dia anterior`,
    positive,
  };
}

export function computeCollectionRate(paid: number, pending: number): number {
  const total = paid + pending;
  if (total === 0) return 100;
  return Math.round((paid / total) * 100);
}

export function clampProgress(value: number): number {
  return Math.min(100, Math.max(0, Math.round(value)));
}

export function toChartPoints(series: Array<{ data: string; valor: number }>, limit = 14) {
  return series.slice(-limit).map((point) => ({
    name: formatChartDate(point.data),
    value: point.valor,
  }));
}
