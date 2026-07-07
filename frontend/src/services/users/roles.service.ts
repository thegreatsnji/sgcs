import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type { Permission, Role } from "@/types/user-management";
import { unwrapApiData } from "@/utils/api-response";

export const rolesService = {
  list: async () => {
    const { data } = await api.get<ApiEnvelope<PaginatedResponse<Role>>>("/users/roles/");
    return unwrapApiData(data);
  },

  get: async (id: number) => {
    const { data } = await api.get<ApiEnvelope<Role>>(`/users/roles/${id}/`);
    return unwrapApiData(data);
  },

  create: async (payload: Partial<Role> & { permission_ids?: number[] }) => {
    const { data } = await api.post<ApiEnvelope<Role>>("/users/roles/", payload);
    return unwrapApiData(data);
  },

  update: async (id: number, payload: Partial<Role> & { permission_ids?: number[] }) => {
    const { data } = await api.patch<ApiEnvelope<Role>>(`/users/roles/${id}/`, payload);
    return unwrapApiData(data);
  },
};

export const permissionsService = {
  list: async () => {
    const { data } = await api.get<ApiEnvelope<PaginatedResponse<Permission>>>("/users/permissions/");
    return unwrapApiData(data);
  },
};
