import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type { DashboardNotificacoes, Notificacao, PreferenciaNotificacao, TemplateEmail } from "@/types/notifications";
import { unwrapApiData } from "@/utils/api-response";

async function getPaginated<T>(url: string, params?: object) {
  const { data } = await api.get<ApiEnvelope<PaginatedResponse<T>>>(url, { params });
  return unwrapApiData(data);
}

export const notificationsService = {
  list: () => getPaginated<Notificacao>("/notifications/"),
  unread: async () => {
    const { data } = await api.get<ApiEnvelope<{ contador: number; notificacoes: Notificacao[] }>>(
      "/notifications/unread/",
    );
    return unwrapApiData(data);
  },
  markRead: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<Notificacao>>(`/notifications/${id}/read/`);
    return unwrapApiData(data);
  },
  archive: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<Notificacao>>(`/notifications/${id}/archive/`);
    return unwrapApiData(data);
  },
  history: async () => {
    const { data } = await api.get<ApiEnvelope<{ historico: Notificacao[] }>>("/notifications/history/");
    return unwrapApiData(data);
  },
  getPreferences: async () => {
    const { data } = await api.get<ApiEnvelope<PreferenciaNotificacao>>("/notifications/preferences/");
    return unwrapApiData(data);
  },
  updatePreferences: async (payload: Partial<PreferenciaNotificacao>) => {
    const { data } = await api.patch<ApiEnvelope<PreferenciaNotificacao>>("/notifications/preferences/", payload);
    return unwrapApiData(data);
  },
  listEmailTemplates: () => getPaginated<TemplateEmail>("/notifications/templates/email/"),
  getDashboard: async () => {
    const { data } = await api.get<ApiEnvelope<DashboardNotificacoes>>("/dashboard/notifications/");
    return unwrapApiData(data);
  },
  sendTestEmail: async (destinatario: string) => {
    const { data } = await api.post<ApiEnvelope<Record<string, unknown>>>("/notifications/email/test/", {
      destinatario,
    });
    return unwrapApiData(data);
  },
  emailHistory: async () => {
    const { data } = await api.get<ApiEnvelope<Record<string, unknown>[]>>("/notifications/email/history/");
    return unwrapApiData(data);
  },
  smsHistory: async () => {
    const { data } = await api.get<ApiEnvelope<Record<string, unknown>[]>>("/notifications/sms/history/");
    return unwrapApiData(data);
  },
};
