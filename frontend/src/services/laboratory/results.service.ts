import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type { LaboratoryResult, ParametroResultado } from "@/types/laboratoryResult";
import { unwrapApiData } from "@/utils/api-response";

async function getPaginated<T>(url: string, params?: object) {
  const { data } = await api.get<ApiEnvelope<PaginatedResponse<T>>>(url, { params });
  return unwrapApiData(data);
}

async function getOne<T>(url: string) {
  const { data } = await api.get<ApiEnvelope<T>>(url);
  return unwrapApiData(data);
}

export interface CreateResultPayload {
  pedido_laboratorial: number;
  observacoes?: string;
  conclusao?: string;
  parametros?: ParametroResultado[];
}

export const laboratoryResultsService = {
  list: async (params?: object) =>
    getPaginated<LaboratoryResult>("/laboratory/results/", params),

  get: async (id: number) => getOne<LaboratoryResult>(`/laboratory/results/${id}/`),

  create: async (payload: CreateResultPayload) => {
    const { data } = await api.post<ApiEnvelope<LaboratoryResult>>(
      "/laboratory/results/",
      payload,
    );
    return unwrapApiData(data);
  },

  update: async (id: number, payload: { observacoes?: string; conclusao?: string }) => {
    const { data } = await api.patch<ApiEnvelope<LaboratoryResult>>(
      `/laboratory/results/${id}/`,
      payload,
    );
    return unwrapApiData(data);
  },

  validate: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<LaboratoryResult>>(
      `/laboratory/results/${id}/validate/`,
    );
    return unwrapApiData(data);
  },

  publish: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<LaboratoryResult>>(
      `/laboratory/results/${id}/publish/`,
    );
    return unwrapApiData(data);
  },

  addParameter: async (id: number, parametro: ParametroResultado) => {
    const { data } = await api.post<ApiEnvelope<LaboratoryResult>>(
      `/laboratory/results/${id}/parameters/`,
      parametro,
    );
    return unwrapApiData(data);
  },

  uploadAttachment: async (id: number, file: File, descricao?: string) => {
    const form = new FormData();
    form.append("file", file);
    if (descricao) form.append("descricao", descricao);
    const { data } = await api.post<ApiEnvelope<{ resultado: LaboratoryResult; anexo: unknown }>>(
      `/laboratory/results/${id}/attachments/`,
      form,
      { headers: { "Content-Type": "multipart/form-data" } },
    );
    return unwrapApiData(data);
  },

  downloadUrl: (resultId: number, anexoId: number) =>
    `/api/v1/laboratory/results/${resultId}/download/?anexo_id=${anexoId}`,
};
