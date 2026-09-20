export interface Notificacao {
  id: number;
  titulo: string;
  mensagem: string;
  tipo: string;
  canal: string;
  estado: string;
  evento_origem?: string;
  metadados?: Record<string, unknown>;
  lida: boolean;
  arquivada: boolean;
  created_at: string;
}

export interface PreferenciaNotificacao {
  receber_email: boolean;
  receber_sms: boolean;
  receber_internas: boolean;
  receber_lembretes: boolean;
  receber_alertas_admin: boolean;
}

export interface TemplateEmail {
  id: number;
  codigo: string;
  nome: string;
  assunto: string;
  corpo: string;
  activo: boolean;
}

export interface DashboardNotificacoes {
  total: number;
  nao_lidas: number;
  emails_hoje: number;
  sms_hoje: number;
  falhas: number;
  fila_pendente: number;
}
