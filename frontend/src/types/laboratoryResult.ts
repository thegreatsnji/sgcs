export type ResultadoEstado =
  | "EM_PROCESSAMENTO"
  | "RESULTADO_PENDENTE"
  | "VALIDADO"
  | "ENTREGUE";

export interface ParametroResultado {
  id?: number;
  nome: string;
  valor: string;
  unidade: string;
  valor_minimo: string;
  valor_maximo: string;
  interpretacao: string;
  ordem?: number;
}

export interface AnexoResultado {
  id: number;
  tipo: string;
  descricao: string;
  nome_ficheiro: string;
  ficheiro_url: string | null;
  created_at?: string;
}

export interface LaboratoryResult {
  id: number;
  pedido_laboratorial: number;
  numero_pedido: string;
  paciente_id: number;
  paciente_nome: string;
  consulta_id: number;
  medico_nome: string | null;
  estado: ResultadoEstado;
  responsavel: number | null;
  responsavel_nome: string | null;
  validado_por: number | null;
  validado_por_nome: string | null;
  data_resultado: string | null;
  data_validacao: string | null;
  data_publicacao: string | null;
  observacoes: string;
  conclusao: string;
  parametros: ParametroResultado[];
  anexos: AnexoResultado[];
  editavel: boolean;
  created_at: string;
  updated_at: string;
}

export interface LaboratoryResultSummary {
  resultados_pendentes: number;
  resultados_validados: number;
  resultados_entregues_hoje: number;
  tempo_medio_validacao_minutos: number;
  exames_por_tecnico: Array<{ tecnico: string; total: number }>;
  exames_por_dia: Array<{ data: string | null; total: number }>;
}

export interface ClinicalLaboratoryResult {
  id: number;
  pedido_laboratorial_id: number;
  numero_pedido: string;
  estado: ResultadoEstado;
  data_resultado: string | null;
  data_validacao: string | null;
  responsavel: string | null;
  conclusao: string;
  observacoes: string;
  parametros: ParametroResultado[];
  anexos: AnexoResultado[];
}
