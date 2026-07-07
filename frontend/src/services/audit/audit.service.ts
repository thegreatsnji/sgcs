import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type { AuditLog } from "@/types/user-management";
import { unwrapApiData } from "@/utils/api-response";

export const auditService = {
  list: async (params?: Record<string, string | number | undefined>) => {
    const { data } = await api.get<ApiEnvelope<PaginatedResponse<AuditLog>>>("/audit-logs/", {
      params,
    });
    return unwrapApiData(data);
  },
};
