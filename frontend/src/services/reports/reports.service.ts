import { api } from "@/services/api/client";
import type { ApiEnvelope } from "@/types/api";
import type { ChartSeries, ExecutiveDashboard, ReportFilters, ReportSummary } from "@/types/reports";
import { unwrapApiData } from "@/utils/api-response";

export const reportsService = {
  getPatientsReport: async (params?: ReportFilters) => {
    const { data } = await api.get<ApiEnvelope<ReportSummary>>("/reports/patients/", { params });
    return unwrapApiData(data);
  },
  getAppointmentsReport: async (params?: ReportFilters) => {
    const { data } = await api.get<ApiEnvelope<ReportSummary>>("/reports/appointments/", { params });
    return unwrapApiData(data);
  },
  getLaboratoryReport: async (params?: ReportFilters) => {
    const { data } = await api.get<ApiEnvelope<ReportSummary>>("/reports/laboratory/", { params });
    return unwrapApiData(data);
  },
  getBillingReport: async (params?: ReportFilters) => {
    const { data } = await api.get<ApiEnvelope<ReportSummary>>("/reports/billing/", { params });
    return unwrapApiData(data);
  },
  getFinanceReport: async (params?: ReportFilters) => {
    const { data } = await api.get<ApiEnvelope<ReportSummary>>("/reports/finance/", { params });
    return unwrapApiData(data);
  },
  getCharts: async () => {
    const { data } = await api.get<ApiEnvelope<ChartSeries>>("/reports/charts/");
    return unwrapApiData(data);
  },
  getExecutiveDashboard: async () => {
    const { data } = await api.get<ApiEnvelope<ExecutiveDashboard>>("/dashboard/executive/");
    return unwrapApiData(data);
  },
  exportReport: (tipo: string, formato: "pdf" | "xlsx" | "csv", params?: ReportFilters) =>
    api.get(`/reports/${tipo}/`, { params: { ...params, export: formato }, responseType: "blob" }),
};
