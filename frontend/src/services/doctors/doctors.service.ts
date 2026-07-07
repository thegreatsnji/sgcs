import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type { EvolucaoClinica, HistoricoTerapeutico, Prescricao, Tratamento } from "@/types/doctors";
import { unwrapApiData } from "@/utils/api-response";

async function getPaginated<T>(url: string, params?: object) {
  const { data } = await api.get<ApiEnvelope<PaginatedResponse<T>>>(url, { params });
  return unwrapApiData(data);
}

export const doctorsService = {
  listPrescriptions: () => getPaginated<Prescricao>("/prescriptions/"),
  createPrescription: async (payload: object) => {
    const { data } = await api.post<ApiEnvelope<Prescricao>>("/prescriptions/", payload);
    return unwrapApiData(data);
  },
  approvePrescription: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<Prescricao>>(`/prescriptions/${id}/approve/`);
    return unwrapApiData(data);
  },
  listTreatments: () => getPaginated<Tratamento>("/treatments/"),
  finishTreatment: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<Tratamento>>(`/treatments/${id}/finish/`);
    return unwrapApiData(data);
  },
  listEvolutions: () => getPaginated<EvolucaoClinica>("/evolutions/"),
  createEvolution: async (payload: object) => {
    const { data } = await api.post<ApiEnvelope<EvolucaoClinica>>("/evolutions/", payload);
    return unwrapApiData(data);
  },
  getHistory: async (pacienteId: number) => {
    const { data } = await api.get<ApiEnvelope<HistoricoTerapeutico>>("/prescriptions/history/", {
      params: { paciente_id: pacienteId },
    });
    return unwrapApiData(data);
  },
  createDischarge: async (payload: object) => {
    const { data } = await api.post<ApiEnvelope<Record<string, unknown>>>("/discharges/", payload);
    return unwrapApiData(data);
  },
  createFollowup: async (payload: object) => {
    const { data } = await api.post<ApiEnvelope<Record<string, unknown>>>("/followups/", payload);
    return unwrapApiData(data);
  },
};
