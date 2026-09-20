import type { ClinicalLaboratoryResult } from "@/types/laboratoryResult";

export interface ClinicalPatientSummary {
  id: number;
  full_name: string;
  patient_number: string;
  age?: number;
  gender: string;
  blood_type: string;
  phone: string | null;
  email: string | null;
  photo_url: string | null;
  allergies: Array<{
    id: number;
    allergen: string;
    severity: string;
    reaction: string;
  }>;
  chronic_diseases: Array<{
    id: number;
    disease_name: string;
    icd_code: string;
    status: string;
  }>;
}

export interface VitalSigns {
  id?: number;
  pressao_arterial: string;
  frequencia_cardiaca: number | null;
  frequencia_respiratoria: number | null;
  temperatura: number | null;
  saturacao_oxigenio: number | null;
  peso: number | null;
  altura: number | null;
  imc: number | null;
  observacoes: string;
}

export interface SOAPNote {
  id?: number;
  subjetivo: string;
  objetivo: string;
  avaliacao: string;
  plano: string;
}

export interface ClinicalDiagnosis {
  id: number;
  codigo_cid10: string;
  descricao: string;
  tipo: "PRINCIPAL" | "SECUNDARIO";
}

export interface ExamOrder {
  id: number;
  tipo_exame: string;
  prioridade: string;
  observacoes: string;
  estado: string;
  estado_faturacao?: string;
  estado_faturacao_label?: string;
  servico_id?: number | null;
  servico_nome?: string | null;
  created_at: string;
}

export interface FollowUp {
  id?: number;
  data_retorno: string;
  motivo: string;
  observacoes: string;
}

export interface ClinicalRecord {
  consulta: {
    id: number;
    appointment_number: string;
    status: string;
    chief_complaint: string;
    notes: string;
    diagnosis: string;
    clinical_notes: string;
    started_at: string | null;
    editavel: boolean;
  };
  paciente: ClinicalPatientSummary;
  sinais_vitais: VitalSigns | null;
  /** Vitais do check-in/triagem (read-only no prontuário). */
  sinais_vitais_triagem?: VitalSigns | null;
  anotacao_soap: SOAPNote | null;
  diagnosticos: ClinicalDiagnosis[];
  pedidos_laboratorio: ExamOrder[];
  resultados_laboratoriais: ClinicalLaboratoryResult[];
  pedidos_imagiologia: ExamOrder[];
  seguimento: FollowUp | null;
  ultimas_consultas: Array<{
    id: number;
    appointment_number: string;
    scheduled_at: string;
    status: string;
    doctor: string | null;
    diagnosis: string;
  }>;
  ultimos_pedidos_laboratorio: Array<Record<string, unknown>>;
  ultimos_pedidos_imagiologia: Array<Record<string, unknown>>;
}

export type LaboratoryCatalogItem = {
  id: number;
  codigo: string;
  nome: string;
};

export type ClinicalTab =
  | "resumo"
  | "vitais"
  | "soap"
  | "diagnosticos"
  | "laboratorio"
  | "resultados_laboratorio"
  | "prescricao"
  | "imagiologia"
  | "seguimento"
  | "historico";
