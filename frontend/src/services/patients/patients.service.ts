import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type {
  AuditTrailEntry,
  DuplicateCheckParams,
  DuplicateCheckResult,
  PatientAllergy,
  PatientChronicDisease,
  PatientDetail,
  PatientDocument,
  PatientEmergencyContact,
  PatientFilters,
  PatientHistoryEntry,
  PatientHistoryFilters,
  PatientListItem,
  PatientObservation,
  PatientPayload,
  PatientPhoto,
} from "@/types/patient";
import { unwrapApiData } from "@/utils/api-response";

function patientPath(patientId: number) {
  return `/patients/${patientId}`;
}

async function getPaginated<T>(url: string, params?: object) {
  const { data } = await api.get<ApiEnvelope<PaginatedResponse<T>>>(url, { params });
  return unwrapApiData(data);
}

async function getOne<T>(url: string) {
  const { data } = await api.get<ApiEnvelope<T>>(url);
  return unwrapApiData(data);
}

async function postOne<T>(url: string, payload?: unknown) {
  const { data } = await api.post<ApiEnvelope<T>>(url, payload);
  return unwrapApiData(data);
}

async function patchOne<T>(url: string, payload: unknown) {
  const { data } = await api.patch<ApiEnvelope<T>>(url, payload);
  return unwrapApiData(data);
}

export const patientsService = {
  list: async (params?: PatientFilters) => getPaginated<PatientListItem>("/patients/", params),

  get: async (id: number) => getOne<PatientDetail>(`/patients/${id}/`),

  create: async (payload: PatientPayload) => postOne<PatientDetail>("/patients/", payload),

  update: async (id: number, payload: Partial<PatientPayload>) =>
    patchOne<PatientDetail>(`/patients/${id}/`, payload),

  remove: async (id: number) => {
    const { data } = await api.delete<ApiEnvelope<null>>(`/patients/${id}/`);
    return data;
  },

  activate: async (id: number) => postOne<PatientDetail>(`/patients/${id}/activate/`),

  deactivate: async (id: number) =>
    postOne<{ id: number; is_active: boolean }>(`/patients/${id}/deactivate/`),

  checkDuplicate: async (params: DuplicateCheckParams) => {
    const { data } = await api.get<ApiEnvelope<DuplicateCheckResult>>(
      "/patients/check-duplicate/",
      { params },
    );
    return unwrapApiData(data);
  },

  export: async (exportFormat: string) => {
    const { data } = await api.get<ApiEnvelope<{ formats: string[]; ready: boolean }>>(
      "/patients/export/",
      { params: { export_format: exportFormat } },
    );
    return unwrapApiData(data);
  },

  print: async (id: number) =>
    getOne<{ ready: boolean; patient_id: number }>(`/patients/${id}/print/`),

  listEmergencyContacts: async (patientId: number, params?: Record<string, unknown>) =>
    getPaginated<PatientEmergencyContact>(
      `${patientPath(patientId)}/emergency-contacts/`,
      params,
    ),

  createEmergencyContact: async (
    patientId: number,
    payload: Omit<PatientEmergencyContact, "id" | "created_at" | "updated_at" | "is_active">,
  ) => postOne<PatientEmergencyContact>(`${patientPath(patientId)}/emergency-contacts/`, payload),

  listAllergies: async (patientId: number, params?: Record<string, unknown>) =>
    getPaginated<PatientAllergy>(`${patientPath(patientId)}/allergies/`, params),

  createAllergy: async (patientId: number, payload: Omit<PatientAllergy, "id" | "created_at" | "updated_at" | "is_active" | "recorded_by">) =>
    postOne<PatientAllergy>(`${patientPath(patientId)}/allergies/`, payload),

  updateAllergy: async (patientId: number, id: number, payload: Partial<PatientAllergy>) =>
    patchOne<PatientAllergy>(`${patientPath(patientId)}/allergies/${id}/`, payload),

  deleteAllergy: async (patientId: number, id: number) => {
    const { data } = await api.delete<ApiEnvelope<null>>(
      `${patientPath(patientId)}/allergies/${id}/`,
    );
    return data;
  },

  listChronicDiseases: async (patientId: number, params?: Record<string, unknown>) =>
    getPaginated<PatientChronicDisease>(`${patientPath(patientId)}/chronic-diseases/`, params),

  createChronicDisease: async (
    patientId: number,
    payload: Omit<PatientChronicDisease, "id" | "created_at" | "updated_at" | "is_active" | "recorded_by">,
  ) => postOne<PatientChronicDisease>(`${patientPath(patientId)}/chronic-diseases/`, payload),

  updateChronicDisease: async (patientId: number, id: number, payload: Partial<PatientChronicDisease>) =>
    patchOne<PatientChronicDisease>(`${patientPath(patientId)}/chronic-diseases/${id}/`, payload),

  deleteChronicDisease: async (patientId: number, id: number) => {
    const { data } = await api.delete<ApiEnvelope<null>>(
      `${patientPath(patientId)}/chronic-diseases/${id}/`,
    );
    return data;
  },

  listDocuments: async (patientId: number, params?: Record<string, unknown>) =>
    getPaginated<PatientDocument>(`${patientPath(patientId)}/documents/`, params),

  uploadDocument: async (patientId: number, formData: FormData) => {
    const { data } = await api.post<ApiEnvelope<PatientDocument>>(
      `${patientPath(patientId)}/documents/`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } },
    );
    return unwrapApiData(data);
  },

  deleteDocument: async (patientId: number, id: number) => {
    const { data } = await api.delete<ApiEnvelope<null>>(
      `${patientPath(patientId)}/documents/${id}/`,
    );
    return data;
  },

  listPhotos: async (patientId: number, params?: Record<string, unknown>) =>
    getPaginated<PatientPhoto>(`${patientPath(patientId)}/photos/`, params),

  uploadPhoto: async (patientId: number, formData: FormData) => {
    const { data } = await api.post<ApiEnvelope<PatientPhoto>>(
      `${patientPath(patientId)}/photos/`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } },
    );
    return unwrapApiData(data);
  },

  setPrimaryPhoto: async (patientId: number, id: number) =>
    postOne<PatientPhoto>(`${patientPath(patientId)}/photos/${id}/set-primary/`),

  listObservations: async (patientId: number, params?: Record<string, unknown>) =>
    getPaginated<PatientObservation>(`${patientPath(patientId)}/observations/`, params),

  createObservation: async (
    patientId: number,
    payload: Omit<PatientObservation, "id" | "created_at" | "updated_at" | "is_active" | "created_by" | "updated_by">,
  ) => postOne<PatientObservation>(`${patientPath(patientId)}/observations/`, payload),

  updateObservation: async (patientId: number, id: number, payload: Partial<PatientObservation>) =>
    patchOne<PatientObservation>(`${patientPath(patientId)}/observations/${id}/`, payload),

  deleteObservation: async (patientId: number, id: number) => {
    const { data } = await api.delete<ApiEnvelope<null>>(
      `${patientPath(patientId)}/observations/${id}/`,
    );
    return data;
  },

  pinObservation: async (patientId: number, id: number) =>
    postOne<PatientObservation>(`${patientPath(patientId)}/observations/${id}/pin/`),

  unpinObservation: async (patientId: number, id: number) =>
    postOne<PatientObservation>(`${patientPath(patientId)}/observations/${id}/unpin/`),

  listHistory: async (patientId: number, params?: PatientHistoryFilters) =>
    getPaginated<PatientHistoryEntry>(`${patientPath(patientId)}/history/`, params),

  listAuditTrail: async (patientId: number, params?: Record<string, unknown>) =>
    getPaginated<AuditTrailEntry>(`${patientPath(patientId)}/audit-trail/`, params),
};
