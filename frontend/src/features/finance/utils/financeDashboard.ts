export interface CashFlowData {
  receitas_hoje: number;
  receitas_mes: number;
  despesas_hoje: number;
  despesas_mes: number;
  saldo_diario: number;
  saldo_mensal: number;
  saldo_actual_caixas: number;
  fluxo_diario: { entradas: number; saidas: number };
  fluxo_mensal: { entradas: number; saidas: number };
}

export function parseCashFlow(fluxo: Record<string, unknown>): CashFlowData {
  const fluxoDiario = fluxo.fluxo_diario as { entradas?: number; saidas?: number } | undefined;
  const fluxoMensal = fluxo.fluxo_mensal as { entradas?: number; saidas?: number } | undefined;

  return {
    receitas_hoje: Number(fluxo.receitas_hoje ?? 0),
    receitas_mes: Number(fluxo.receitas_mes ?? 0),
    despesas_hoje: Number(fluxo.despesas_hoje ?? 0),
    despesas_mes: Number(fluxo.despesas_mes ?? 0),
    saldo_diario: Number(fluxo.saldo_diario ?? 0),
    saldo_mensal: Number(fluxo.saldo_mensal ?? 0),
    saldo_actual_caixas: Number(fluxo.saldo_actual_caixas ?? 0),
    fluxo_diario: {
      entradas: Number(fluxoDiario?.entradas ?? 0),
      saidas: Number(fluxoDiario?.saidas ?? 0),
    },
    fluxo_mensal: {
      entradas: Number(fluxoMensal?.entradas ?? 0),
      saidas: Number(fluxoMensal?.saidas ?? 0),
    },
  };
}

export function formatFinanceCurrency(value: number): string {
  return `${value.toLocaleString("pt-PT")} FCFA`;
}
