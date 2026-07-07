export interface ReportSummary {
  tipo: string;
  periodo: string;
  data_inicio: string;
  data_fim: string;
  resumo: Record<string, number | string>;
  demografia?: Record<string, unknown>;
  series?: ChartSeries;
}

export interface ChartSeries {
  receitas: Array<{ data: string; valor: number }>;
  consultas: Array<{ data: string; valor: number }>;
  pacientes: Array<{ data: string; valor: number }>;
  laboratorio: Array<{ data: string; valor: number }>;
  pagamentos: Array<{ data: string; valor: number }>;
}

export interface ExecutiveDashboard {
  indicadores: {
    receita_mensal: number;
    lucro: number;
    pacientes_novos: number;
    consultas: number;
    exames: number;
    tempo_medio_consulta_min: number;
    pagamentos_confirmados: number;
  };
  top_medicos: Array<{ medico: string; total: number }>;
  top_servicos: Array<{ nome: string; quantidade: number }>;
  top_exames: Array<{ nome: string; total: number }>;
  graficos: ChartSeries;
}

export type ReportPeriod = "hoje" | "semana" | "mes" | "ano" | "personalizado";

export interface ReportFilters {
  periodo?: ReportPeriod;
  data_inicio?: string;
  data_fim?: string;
  medico_id?: number;
  paciente_id?: number;
  estado?: string;
  categoria?: string;
}
