import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type { ManagedUser, UserFilters, UserPayload } from "@/types/user-management";
import { unwrapApiData } from "@/utils/api-response";

export const usersService = {
  list: async (params?: UserFilters) => {
    const { data } = await api.get<ApiEnvelope<PaginatedResponse<ManagedUser>>>("/users/accounts/", {
      params,
    });
    return unwrapApiData(data);
  },

  get: async (id: number) => {
    const { data } = await api.get<ApiEnvelope<ManagedUser>>(`/users/accounts/${id}/`);
    return unwrapApiData(data);
  },

  create: async (payload: UserPayload) => {
    const { data } = await api.post<ApiEnvelope<ManagedUser>>("/users/accounts/", payload);
    return unwrapApiData(data);
  },

  update: async (id: number, payload: Partial<UserPayload>) => {
    const { data } = await api.patch<ApiEnvelope<ManagedUser>>(`/users/accounts/${id}/`, payload);
    return unwrapApiData(data);
  },

  remove: async (id: number) => {
    const { data } = await api.delete<ApiEnvelope<null>>(`/users/accounts/${id}/`);
    return data;
  },

  activate: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<null>>(`/users/accounts/${id}/activate/`);
    return data;
  },

  deactivate: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<null>>(`/users/accounts/${id}/deactivate/`);
    return data;
  },

  getProfile: async () => {
    const { data } = await api.get<ApiEnvelope<ManagedUser & { permissions: string[] }>>("/users/profile/");
    return unwrapApiData(data);
  },

  updateProfile: async (payload: FormData | Partial<UserPayload>) => {
    const { data } = await api.patch<ApiEnvelope<ManagedUser>>("/users/profile/", payload, {
      headers: payload instanceof FormData ? { "Content-Type": "multipart/form-data" } : undefined,
    });
    return unwrapApiData(data);
  },

  changePassword: async (payload: {
    old_password: string;
    new_password: string;
    new_password_confirm: string;
  }) => {
    const { data } = await api.post<ApiEnvelope<null>>("/users/profile/password/", payload);
    return data;
  },

  getSessions: async () => {
    const { data } = await api.get<ApiEnvelope<PaginatedResponse<UserSession>>>("/users/profile/sessions/");
    return unwrapApiData(data);
  },

  getAccessHistory: async () => {
    const { data } = await api.get<ApiEnvelope<PaginatedResponse<AccessHistoryItem>>>(
      "/users/profile/access-history/",
    );
    return unwrapApiData(data);
  },

  exportUsers: async (format: string) => {
    const { data } = await api.get<ApiEnvelope<{ formats: string[]; ready: boolean }>>(
      "/users/accounts/export/",
      { params: { format } },
    );
    return unwrapApiData(data);
  },
};

export interface UserSession {
  id: number;
  ip_address: string | null;
  user_agent: string;
  is_active: boolean;
  created_at: string;
  last_activity: string;
  logged_out_at: string | null;
}

export interface AccessHistoryItem {
  id: number;
  action: string;
  description: string;
  ip_address: string | null;
  created_at: string;
}
