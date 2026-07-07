import type { BaseEntity, UserSummary } from "./common";
import type { PaginationParams } from "./api";

export type PatientGender = "M" | "F" | "O";
export type DocumentType = "BI" | "PASSAPORTE" | "CARTAO_RESIDENTE" | "OUTRO";
export type BloodType =
  | "A+"
  | "A-"
  | "B+"
  | "B-"
  | "AB+"
  | "AB-"
  | "O+"
  | "O-"
  | "DESCONHECIDO";
export type MaritalStatus = "SOLTEIRO" | "CASADO" | "DIVORCIADO" | "VIUVO" | "OUTRO";
export type EmergencyRelationship =
  | "CONJUGE"
  | "PAI"
  | "MAE"
  | "FILHO"
  | "IRMAO"
  | "AMIGO"
  | "OUTRO";
export type AllergySeverity = "LEVE" | "MODERADA" | "GRAVE" | "ANAFILAXIA";
export type ChronicDiseaseStatus = "ATIVA" | "CONTROLADA" | "REMISSAO" | "CURADA";
export type PatientDocumentType =
  | "BI"
  | "PASSAPORTE"
  | "CARTAO_SEGURO"
  | "CONSENTIMENTO"
  | "EXAME_EXTERNO"
  | "DECLARACAO"
  | "OUTRO";
export type HistoryEventType =
  | "REGISTO"
  | "ADMISSAO"
  | "ALTA"
  | "CONSULTA"
  | "EXAME"
  | "DIAGNOSTICO"
  | "CIRURGIA"
  | "MEDICACAO"
  | "ALERGIA"
  | "DOENCA_CRONICA"
  | "DOCUMENTO"
  | "OBSERVACAO"
  | "PAGAMENTO"
  | "OUTRO";
export type ObservationType = "CLINICA" | "ENFERMAGEM" | "ADMINISTRATIVA";

export interface PatientListItem extends BaseEntity {
  patient_number: string;
  full_name: string;
  first_name: string;
  last_name: string;
  document_number?: string | null;
  document_type?: DocumentType | null;
  phone?: string | null;
  email?: string | null;
  birth_date?: string | null;
  gender?: PatientGender | null;
  is_active: boolean;
}

export interface PatientEmergencyContact extends BaseEntity {
  name: string;
  phone: string;
  email?: string | null;
  relationship: EmergencyRelationship;
  is_primary: boolean;
  is_active: boolean;
}

export interface PatientDetail extends PatientListItem {
  age?: number;
  address_street?: string | null;
  address_city?: string | null;
  address_region?: string | null;
  address_country?: string | null;
  address_postal_code?: string | null;
  nationality?: string | null;
  blood_type?: BloodType | null;
  marital_status?: MaritalStatus | null;
  occupation?: string | null;
  is_deleted?: boolean;
  deleted_at?: string | null;
  created_by?: UserSummary | null;
  updated_by?: UserSummary | null;
  emergency_contacts?: PatientEmergencyContact[];
  allergies_count?: number;
  chronic_diseases_count?: number;
  primary_photo_url?: string | null;
}

export interface PatientPayload {
  first_name: string;
  last_name: string;
  document_type?: DocumentType | null;
  document_number?: string | null;
  birth_date: string;
  gender: PatientGender;
  phone: string;
  email?: string | null;
  address_street?: string | null;
  address_city?: string | null;
  address_region?: string | null;
  address_country?: string | null;
  address_postal_code?: string | null;
  nationality?: string | null;
  blood_type?: BloodType | null;
  marital_status?: MaritalStatus | null;
  occupation?: string | null;
  emergency_contacts?: Omit<PatientEmergencyContact, "id" | "created_at" | "updated_at" | "is_active">[];
}

export interface PatientFilters extends PaginationParams {
  is_active?: boolean;
  gender?: PatientGender;
  document_type?: DocumentType;
  blood_type?: BloodType;
  has_allergies?: boolean;
  has_chronic_diseases?: boolean;
}

export interface DuplicateCheckParams {
  first_name: string;
  last_name: string;
  birth_date: string;
  phone?: string;
  document_number?: string;
}

export interface DuplicateMatch {
  id: number;
  patient_number: string;
  full_name: string;
  birth_date: string;
  phone?: string | null;
  document_number?: string | null;
  similarity_score: number;
}

export interface DuplicateCheckResult {
  has_duplicates: boolean;
  matches: DuplicateMatch[];
}

export interface PatientAllergy extends BaseEntity {
  allergen: string;
  severity: AllergySeverity;
  reaction?: string | null;
  diagnosed_at?: string | null;
  is_active: boolean;
  notes?: string | null;
  recorded_by?: UserSummary | null;
}

export interface PatientChronicDisease extends BaseEntity {
  disease_name: string;
  icd_code?: string | null;
  diagnosed_at?: string | null;
  status: ChronicDiseaseStatus;
  is_active: boolean;
  notes?: string | null;
  recorded_by?: UserSummary | null;
}

export interface PatientDocument extends BaseEntity {
  document_type: PatientDocumentType;
  title: string;
  document_number?: string | null;
  description?: string | null;
  issued_at?: string | null;
  expires_at?: string | null;
  is_active: boolean;
  file_url?: string | null;
  mime_type?: string | null;
  size?: number | null;
  uploaded_by?: UserSummary | null;
}

export interface PatientPhoto extends BaseEntity {
  title?: string | null;
  is_primary: boolean;
  is_active: boolean;
  file_url?: string | null;
  mime_type?: string | null;
  size?: number | null;
  uploaded_by?: UserSummary | null;
}

export interface PatientObservation extends BaseEntity {
  observation_type: ObservationType;
  content: string;
  is_pinned: boolean;
  is_active: boolean;
  created_by?: UserSummary | null;
  updated_by?: UserSummary | null;
}

export interface PatientHistoryEntry extends BaseEntity {
  event_type: HistoryEventType;
  title: string;
  description?: string | null;
  event_date: string;
  source_module?: string | null;
  source_id?: number | null;
  metadata?: Record<string, unknown>;
  recorded_by?: UserSummary | null;
}

export interface PatientHistoryFilters extends PaginationParams {
  event_type?: HistoryEventType;
  source_module?: string;
}

export interface AuditTrailEntry {
  id: number;
  action: string;
  description: string;
  user: UserSummary | null;
  ip_address: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}
