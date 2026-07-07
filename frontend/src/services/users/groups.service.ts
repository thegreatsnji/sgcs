import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type { UserGroup } from "@/types/user-management";
import { unwrapApiData } from "@/utils/api-response";

export const groupsService = {
  list: async () => {
    const { data } = await api.get<ApiEnvelope<PaginatedResponse<UserGroup>>>("/users/groups/");
    return unwrapApiData(data);
  },

  create: async (payload: Partial<UserGroup> & { permission_ids?: number[]; member_ids?: number[] }) => {
    const { data } = await api.post<ApiEnvelope<UserGroup>>("/users/groups/", payload);
    return unwrapApiData(data);
  },

  update: async (
    id: number,
    payload: Partial<UserGroup> & { permission_ids?: number[]; member_ids?: number[] },
  ) => {
    const { data } = await api.patch<ApiEnvelope<UserGroup>>(`/users/groups/${id}/`, payload);
    return unwrapApiData(data);
  },

  remove: async (id: number) => {
    const { data } = await api.delete<ApiEnvelope<null>>(`/users/groups/${id}/`);
    return data;
  },
};
