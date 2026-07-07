export interface EvolucaoClinica {
  id: number;
  consulta: number;
  tipo: string;
  observacoes: string;
  resposta_tratamento?: string;
  created_at: string;
}

export interface MedicamentoPrescrito {
  id?: number;
  nome: string;
  dosagem: string;
  forma_farmaceutica?: string;
  via?: string;
  frequencia: string;
  duracao: string;
  posologia?: string;
  estado?: string;
}

export interface Prescricao {
  id: number;
  consulta: number;
  paciente: number;
  paciente_nome?: string;
  estado: string;
  observacoes: string;
  medicamentos: MedicamentoPrescrito[];
  created_at: string;
}

export interface Tratamento {
  id: number;
  tipo: string;
  descricao: string;
  estado: string;
  data_inicio: string;
  data_fim?: string;
}

export interface HistoricoTerapeutico {
  prescricoes: Array<{ id: number; estado: string; created_at: string }>;
  tratamentos: Array<{ id: number; tipo: string; estado: string }>;
}
