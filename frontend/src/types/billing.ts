export type OrcamentoEstado = "RASCUNHO" | "PENDENTE" | "APROVADO" | "EXPIRADO";
export type FaturaEstado = "PENDENTE" | "PARCIAL" | "PAGA" | "CANCELADA";
export type PagamentoEstado = "PENDENTE" | "PROCESSADO" | "CONFIRMADO" | "REEMBOLSADO";
export type MetodoPagamento = "DINHEIRO" | "TRANSFERENCIA" | "CARTAO" | "MOBILE_MONEY" | "OUTRO";

export interface BillingService {
  id: number;
  codigo: string;
  nome: string;
  descricao: string;
  categoria: string;
  categoria_label?: string;
  departamento?: number | null;
  departamento_nome?: string | null;
  especialidade?: number | null;
  especialidade_nome?: string | null;
  preco: string;
  moeda?: string;
  activo: boolean;
  exige_pedido_medico?: boolean;
  preco_confirmado?: boolean;
  estado_validacao?: string;
  exige_agendamento?: boolean;
  updated_at?: string;
}

export interface BillingItem {
  id: number;
  servico: number;
  servico_nome: string;
  quantidade: number;
  preco_unitario?: string;
  preco?: string;
  subtotal: string;
}

export interface Quote {
  id: number;
  numero: string;
  paciente: number;
  paciente_nome: string;
  estado: OrcamentoEstado;
  subtotal: string;
  desconto: string;
  imposto: string;
  total: string;
  validade: string | null;
  itens: BillingItem[];
  editavel: boolean;
}

export interface Invoice {
  id: number;
  numero: string;
  paciente: number;
  paciente_nome: string;
  consulta: number | null;
  consulta_numero: string | null;
  orcamento: number | null;
  estado: FaturaEstado;
  subtotal: string;
  desconto: string;
  imposto: string;
  total: string;
  total_pago: string;
  saldo?: string;
  emitida_em: string | null;
  itens: BillingItem[];
  pagamentos: Payment[];
  editavel: boolean;
}

export interface Payment {
  id: number;
  fatura: number;
  fatura_numero: string;
  metodo_pagamento: MetodoPagamento;
  valor: string;
  referencia: string;
  estado: PagamentoEstado;
  data_pagamento: string | null;
}

export interface Receipt {
  id: number;
  numero: string;
  pagamento: number;
  pagamento_valor: string;
  fatura_numero: string;
  paciente_nome: string;
  metodo_pagamento: string;
  emitido_em: string;
}

export interface BillingDashboardData {
  indicadores: {
    receita_hoje: number;
    receita_mensal: number;
    faturas_pendentes: number;
    faturas_pagas: number;
    pagamentos_do_dia: number;
    faturas_emitidas_hoje: number;
  };
  servicos_mais_vendidos: Array<{ servico: string; quantidade: number }>;
}

export type OperationalPeriod = "hoje" | "semana" | "mes" | "personalizado";

export interface OperationalBillingSummary {
  periodo: {
    modo?: OperationalPeriod | string;
    data_inicio: string;
    data_fim: string;
  };
  total_faturado: string;
  total_recebido: string;
  saldo_pendente: string;
  total_reducoes: string;
  numero_pagamentos: number;
}

export interface PatientFinancialHistory {
  paciente_id: number;
  resumo: { total_faturado: string; total_pago: string; saldo: string };
  faturas: Array<{ id: number; numero: string; estado: string; total: string; emitida_em: string | null }>;
  orcamentos: Array<{ id: number; numero: string; estado: string; total: string; validade: string | null }>;
  recibos: Array<{ id: number; numero: string; emitido_em: string; fatura_numero: string; valor: string }>;
}
