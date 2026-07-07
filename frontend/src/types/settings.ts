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
