export interface ClinicProfile {
  id: number;
  nome: string;
  nif: string;
  morada: string;
  cidade: string;
  pais: string;
  telefone: string;
  telemovel: string;
  email: string;
  website: string;
  moeda: string;
  fuso_horario: string;
  idioma: string;
  horario_funcionamento: string;
  dias_uteis: string[];
  mensagem_rodape: string;
}

export interface Specialty {
  id: number;
  codigo: string;
  nome: string;
  descricao: string;
  cor: string;
  activo: boolean;
}

export interface Department {
  id: number;
  codigo: string;
  nome: string;
  descricao: string;
  activo: boolean;
}

export interface FeatureFlag {
  id: number;
  codigo: string;
  nome: string;
  descricao: string;
  activo: boolean;
}

export interface SystemDashboard {
  monitorizacao: Record<string, unknown>;
  backups_recentes: Array<Record<string, unknown>>;
  clinica: ClinicProfile;
  feature_flags: FeatureFlag[];
}

export interface MedicoPerfil {
  id: number;
  utilizador: number;
  utilizador_nome: string;
  utilizador_email: string;
  especialidade: number | null;
  especialidade_nome: string | null;
  departamento: number | null;
  departamento_nome: string | null;
  numero_profissional: string;
  dias_trabalho: string[];
  horario_atendimento: Record<string, string>;
  horario_configurado: boolean;
  duracao_consulta_minutos: number;
  servico_consulta: number | null;
  servico_consulta_nome: string | null;
  servico_consulta_preco: string | null;
  activo: boolean;
  disponivel_marcacao: boolean;
}
