import { api } from "@/services/api/client";
import type { ApiEnvelope } from "@/types/api";
import type { AdminDashboardData, ClinicalDashboardData } from "@/types/user-management";
import type { ConsultationDashboardData } from "@/types/appointment";
import type { ReceptionDashboardData } from "@/types/reception";
import { unwrapApiData } from "@/utils/api-response";

export const dashboardService = {
  getAdminSummary: async () => {
    const { data } = await api.get<ApiEnvelope<AdminDashboardData>>("/dashboard/admin/");
    return unwrapApiData(data);
  },

  getClinicalSummary: async () => {
    const { data } = await api.get<ApiEnvelope<ClinicalDashboardData>>("/dashboard/clinical/");
    return unwrapApiData(data);
  },

  getReceptionSummary: async () => {
    const { data } = await api.get<ApiEnvelope<ReceptionDashboardData>>("/dashboard/reception/");
    return unwrapApiData(data);
  },

  getConsultationSummary: async () => {
    const { data } = await api.get<ApiEnvelope<ConsultationDashboardData>>(
      "/dashboard/consultations/",
    );
    return unwrapApiData(data);
  },
};
