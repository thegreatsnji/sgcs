import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type {
  Appointment,
  AppointmentCreatePayload,
  AppointmentUpdatePayload,
  ConsultasDashboardData,
} from "@/types/appointment";
import type { ClinicalRecord } from "@/types/clinicalRecord";
import { unwrapApiData } from "@/utils/api-response";

async function getPaginated<T>(url: string, params?: object) {
  const { data } = await api.get<ApiEnvelope<PaginatedResponse<T>>>(url, { params });
  return unwrapApiData(data);
}

async function getOne<T>(url: string) {
  const { data } = await api.get<ApiEnvelope<T>>(url);
  return unwrapApiData(data);
}

async function finishAppointment(id: number, payload?: { diagnosis?: string; clinical_notes?: string }) {
  const { data } = await api.post<ApiEnvelope<Appointment>>(`/appointments/${id}/finish/`, payload);
  return unwrapApiData(data);
}

export const appointmentsService = {
  list: async (params?: object) => getPaginated<Appointment>("/appointments/", params),

  get: async (id: number) => getOne<Appointment>(`/appointments/${id}/`),

  getToday: async (params?: { doctor?: number; page?: number }) =>
    getPaginated<Appointment>("/appointments/today/", params),

  getDoctor: async (params?: { doctor_id?: number; date?: string; page?: number }) =>
    getPaginated<Appointment>("/appointments/doctor/", params),

  getQueue: async (params?: { page?: number }) =>
    getPaginated<Appointment>("/appointments/queue/", params),

  getCalendar: async (params: { start: string; end: string; doctor_id?: number }) => {
    const { data } = await api.get<ApiEnvelope<Appointment[]>>("/appointments/calendar/", { params });
    return unwrapApiData(data);
  },

  create: async (payload: AppointmentCreatePayload) => {
    const { data } = await api.post<ApiEnvelope<Appointment>>("/appointments/", payload);
    return unwrapApiData(data);
  },

  update: async (id: number, payload: AppointmentUpdatePayload) => {
    const { data } = await api.patch<ApiEnvelope<Appointment>>(`/appointments/${id}/`, payload);
    return unwrapApiData(data);
  },

  remove: async (id: number) => {
    const { data } = await api.delete<ApiEnvelope<null>>(`/appointments/${id}/`);
    return data;
  },

  confirm: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<Appointment>>(`/appointments/${id}/confirm/`);
    return unwrapApiData(data);
  },

  start: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<Appointment>>(`/appointments/${id}/start/`);
    return unwrapApiData(data);
  },

  finish: finishAppointment,

  /** @deprecated Use finish — mantido para compatibilidade com rotas legadas */
  complete: finishAppointment,

  cancel: async (id: number, reason?: string) => {
    const { data } = await api.post<ApiEnvelope<Appointment>>(`/appointments/${id}/cancel/`, { reason });
    return unwrapApiData(data);
  },

  updateClinical: async (
    id: number,
    payload: {
      chief_complaint?: string;
      notes?: string;
      diagnosis?: string;
      clinical_notes?: string;
      subjetivo?: string;
      objetivo?: string;
      avaliacao?: string;
      plano?: string;
    },
  ) => {
    const { data } = await api.patch<ApiEnvelope<ClinicalRecord>>(`/appointments/${id}/clinical/`, payload);
    return unwrapApiData(data);
  },

  getClinicalRecord: async (id: number) =>
    getOne<ClinicalRecord>(`/appointments/${id}/clinical/`),

  saveVitalSigns: async (id: number, payload: object) => {
    const { data } = await api.post<ApiEnvelope<ClinicalRecord>>(`/appointments/${id}/vital-signs/`, payload);
    return unwrapApiData(data);
  },

  addDiagnosis: async (
    id: number,
    payload: { codigo_cid10: string; descricao: string; tipo?: string },
  ) => {
    const { data } = await api.post<ApiEnvelope<ClinicalRecord>>(`/appointments/${id}/diagnoses/`, payload);
    return unwrapApiData(data);
  },

  addLabOrder: async (id: number, payload: { tipo_exame: string; prioridade?: string; observacoes?: string }) => {
    const { data } = await api.post<ApiEnvelope<ClinicalRecord>>(`/appointments/${id}/laboratory/`, payload);
    return unwrapApiData(data);
  },

  addImagingOrder: async (id: number, payload: { tipo_exame: string; prioridade?: string; observacoes?: string }) => {
    const { data } = await api.post<ApiEnvelope<ClinicalRecord>>(`/appointments/${id}/imaging/`, payload);
    return unwrapApiData(data);
  },

  saveFollowUp: async (id: number, payload: { data_retorno: string; motivo: string; observacoes?: string }) => {
    const { data } = await api.post<ApiEnvelope<ClinicalRecord>>(`/appointments/${id}/follow-up/`, payload);
    return unwrapApiData(data);
  },

  getDashboard: async () => {
    const { data } = await api.get<ApiEnvelope<ConsultasDashboardData>>("/dashboard/consultas/");
    return unwrapApiData(data);
  },
};
