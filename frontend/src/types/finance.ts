export interface FinanceDashboardData {
  indicadores: {
    receita_hoje: number;
    receita_mensal: number;
    despesa_hoje: number;
    despesa_mensal: number;
    lucro: number;
    saldo_actual: number;
    pagamentos_confirmados: number;
    pagamentos_hoje: number;
  };
  fluxo_caixa: Record<string, unknown>;
  top_categorias: Array<{ categoria: string; total: number }>;
  servicos_mais_vendidos: Array<{ servico: string; quantidade: number }>;
}

export interface CashRegister {
  id: number;
  codigo: string;
  nome: string;
  estado: "ABERTO" | "FECHADO";
  saldo_inicial: string;
  saldo_actual: string;
  data_abertura: string | null;
  data_fecho: string | null;
}

export interface FinanceMovement {
  id: number;
  caixa: number;
  caixa_codigo: string;
  tipo: string;
  origem: string;
  valor: string;
  descricao: string;
  data: string;
}

export interface Expense {
  id: number;
  fornecedor: string;
  categoria: string;
  valor: string;
  descricao: string;
  estado: string;
  data: string;
}

export interface FinanceReport {
  tipo: string;
  periodo: string;
  receitas: number;
  despesas: number;
  lucro: number;
  pagamentos: number;
}
