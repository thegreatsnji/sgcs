export type LaboratoryOrderStatus =
  | "PENDENTE"
  | "RECEBIDO"
  | "AGUARDANDO_COLHEITA"
  | "EM_PROCESSAMENTO"
  | "CONCLUIDO"
  | "CANCELADO";

export interface LaboratoryPatientSummary {
  id: number;
  full_name: string;
  patient_number: string;
  phone: string | null;
}

export interface LaboratoryDoctorSummary {
  id: number;
  full_name: string;
}

export interface LaboratoryExam {
  id: number;
  nome_exame: string;
  categoria: string;
  estado: LaboratoryOrderStatus;
  observacoes: string;
  created_at: string;
  updated_at: string;
}

export interface LaboratoryOrder {
  id: number;
  numero_pedido: string;
  consulta_id: number;
  appointment_number: string;
  paciente: LaboratoryPatientSummary;
  medico: LaboratoryDoctorSummary | null;
  estado: LaboratoryOrderStatus;
  prioridade: string;
  data_pedido: string;
  data_rececao: string | null;
  data_colheita: string | null;
  data_conclusao: string | null;
  observacoes: string;
  exames: LaboratoryExam[];
  created_at: string;
  updated_at: string;
}

export interface LaboratoryDashboardData {
  indicadores: {
    pedidos_pendentes: number;
    em_processamento: number;
    concluidos_hoje: number;
    tempo_medio_minutos: number;
  };
  cards: {
    pending: number;
    in_progress: number;
    completed_today: number;
    avg_time_minutes: number;
  };
  resultados?: {
    resultados_pendentes: number;
    resultados_validados: number;
    resultados_entregues_hoje: number;
    tempo_medio_validacao_minutos: number;
    exames_por_tecnico: Array<{ tecnico: string; total: number }>;
    exames_por_dia: Array<{ data: string | null; total: number }>;
  };
}
