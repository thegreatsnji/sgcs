import type {
  AllergySeverity,
  BloodType,
  ChronicDiseaseStatus,
  DocumentType,
  EmergencyRelationship,
  HistoryEventType,
  MaritalStatus,
  ObservationType,
  PatientDocumentType,
  PatientGender,
} from "@/types/patient";

export const PATIENT_GENDER_LABELS: Record<PatientGender, string> = {
  M: "Masculino",
  F: "Feminino",
  O: "Outro",
};

export const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  BI: "Bilhete de Identidade",
  PASSAPORTE: "Passaporte",
  CARTAO_RESIDENTE: "Cartão de residente",
  OUTRO: "Outro",
};

export const BLOOD_TYPE_LABELS: Record<BloodType, string> = {
  "A+": "A+",
  "A-": "A-",
  "B+": "B+",
  "B-": "B-",
  "AB+": "AB+",
  "AB-": "AB-",
  "O+": "O+",
  "O-": "O-",
  DESCONHECIDO: "Desconhecido",
};

export const MARITAL_STATUS_LABELS: Record<MaritalStatus, string> = {
  SOLTEIRO: "Solteiro",
  CASADO: "Casado",
  DIVORCIADO: "Divorciado",
  VIUVO: "Viúvo",
  OUTRO: "Outro",
};

export const EMERGENCY_RELATIONSHIP_LABELS: Record<EmergencyRelationship, string> = {
  CONJUGE: "Cônjuge",
  PAI: "Pai",
  MAE: "Mãe",
  FILHO: "Filho",
  IRMAO: "Irmão",
  AMIGO: "Amigo",
  OUTRO: "Outro",
};

export const ALLERGY_SEVERITY_LABELS: Record<AllergySeverity, string> = {
  LEVE: "Leve",
  MODERADA: "Moderada",
  GRAVE: "Grave",
  ANAFILAXIA: "Anafilaxia",
};

export const CHRONIC_DISEASE_STATUS_LABELS: Record<ChronicDiseaseStatus, string> = {
  ATIVA: "Ativa",
  CONTROLADA: "Controlada",
  REMISSAO: "Remissão",
  CURADA: "Curada",
};

export const PATIENT_DOCUMENT_TYPE_LABELS: Record<PatientDocumentType, string> = {
  BI: "Bilhete de Identidade",
  PASSAPORTE: "Passaporte",
  CARTAO_SEGURO: "Cartão de seguro",
  CONSENTIMENTO: "Consentimento",
  EXAME_EXTERNO: "Exame externo",
  DECLARACAO: "Declaração",
  OUTRO: "Outro",
};

export const HISTORY_EVENT_TYPE_LABELS: Record<HistoryEventType, string> = {
  REGISTO: "Registo",
  ADMISSAO: "Admissão",
  ALTA: "Alta",
  CONSULTA: "Consulta",
  EXAME: "Exame",
  DIAGNOSTICO: "Diagnóstico",
  CIRURGIA: "Cirurgia",
  MEDICACAO: "Medicação",
  ALERGIA: "Alergia",
  DOENCA_CRONICA: "Doença crónica",
  DOCUMENTO: "Documento",
  OBSERVACAO: "Observação",
  PAGAMENTO: "Pagamento",
  OUTRO: "Outro",
};

export const OBSERVATION_TYPE_LABELS: Record<ObservationType, string> = {
  CLINICA: "Clínica",
  ENFERMAGEM: "Enfermagem",
  ADMINISTRATIVA: "Administrativa",
};

export const PATIENT_PAGE_SIZE = 20;
