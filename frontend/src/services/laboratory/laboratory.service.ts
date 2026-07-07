import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type { LaboratoryDashboardData, LaboratoryOrder } from "@/types/laboratory";
import { unwrapApiData } from "@/utils/api-response";

async function getPaginated<T>(url: string, params?: object) {
  const { data } = await api.get<ApiEnvelope<PaginatedResponse<T>>>(url, { params });
  return unwrapApiData(data);
}

async function getOne<T>(url: string) {
  const { data } = await api.get<ApiEnvelope<T>>(url);
  return unwrapApiData(data);
}

export const laboratoryService = {
  list: async (params?: object) => getPaginated<LaboratoryOrder>("/laboratory/", params),

  getPending: async (params?: object) =>
    getPaginated<LaboratoryOrder>("/laboratory/pending/", params),

  getToday: async (params?: object) =>
    getPaginated<LaboratoryOrder>("/laboratory/today/", params),

  getCollectionQueue: async (params?: object) =>
    getPaginated<LaboratoryOrder>("/laboratory/collection-queue/", params),

  get: async (id: number) => getOne<LaboratoryOrder>(`/laboratory/${id}/`),

  update: async (id: number, payload: { observacoes?: string; prioridade?: string }) => {
    const { data } = await api.patch<ApiEnvelope<LaboratoryOrder>>(`/laboratory/${id}/`, payload);
    return unwrapApiData(data);
  },

  receive: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<LaboratoryOrder>>(`/laboratory/${id}/receive/`);
    return unwrapApiData(data);
  },

  collect: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<LaboratoryOrder>>(`/laboratory/${id}/collect/`);
    return unwrapApiData(data);
  },

  start: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<LaboratoryOrder>>(`/laboratory/${id}/start/`);
    return unwrapApiData(data);
  },

  finish: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<LaboratoryOrder>>(`/laboratory/${id}/finish/`);
    return unwrapApiData(data);
  },

  getDashboard: async () => {
    const { data } = await api.get<ApiEnvelope<LaboratoryDashboardData>>("/dashboard/laboratory/");
    return unwrapApiData(data);
  },
};

