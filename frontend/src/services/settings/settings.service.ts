import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type { ClinicProfile, Department, FeatureFlag, Specialty, SystemDashboard } from "@/types/settings";
import { unwrapApiData } from "@/utils/api-response";

async function getPaginated<T>(url: string) {
  const { data } = await api.get<ApiEnvelope<PaginatedResponse<T>>>(url);
  return unwrapApiData(data);
}

export const settingsService = {
  getClinic: async () => {
    const { data } = await api.get<ApiEnvelope<ClinicProfile>>("/settings/clinic/");
    return unwrapApiData(data);
  },
  updateClinic: async (payload: Partial<ClinicProfile>) => {
    const { data } = await api.patch<ApiEnvelope<ClinicProfile>>("/settings/clinic/", payload);
    return unwrapApiData(data);
  },
  listSpecialties: () => getPaginated<Specialty>("/settings/specialties/"),
  listDepartments: () => getPaginated<Department>("/settings/departments/"),
  getBilling: async () => {
    const { data } = await api.get<ApiEnvelope<Record<string, unknown>>>("/settings/billing/");
    return unwrapApiData(data);
  },
  getSecurity: async () => {
    const { data } = await api.get<ApiEnvelope<Record<string, unknown>>>("/settings/security/");
    return unwrapApiData(data);
  },
  updateSecurity: async (payload: object) => {
    const { data } = await api.patch<ApiEnvelope<Record<string, unknown>>>("/settings/security/", payload);
    return unwrapApiData(data);
  },
  getEmail: async () => {
    const { data } = await api.get<ApiEnvelope<Record<string, unknown>>>("/settings/email/");
    return unwrapApiData(data);
  },
  getFeatureFlags: async () => {
    const { data } = await api.get<ApiEnvelope<FeatureFlag[]>>("/settings/feature-flags/");
    return unwrapApiData(data);
  },
  updateFeatureFlag: async (codigo: string, activo: boolean) => {
    const { data } = await api.patch<ApiEnvelope<FeatureFlag>>("/settings/feature-flags/", { codigo, activo });
    return unwrapApiData(data);
  },
  getSystemDashboard: async () => {
    const { data } = await api.get<ApiEnvelope<SystemDashboard>>("/dashboard/system/");
    return unwrapApiData(data);
  },
  listBackups: () => getPaginated<Record<string, unknown>>("/settings/backups/"),
  createBackup: async () => {
    const { data } = await api.post<ApiEnvelope<Record<string, unknown>>>("/settings/backups/", { tipo: "MANUAL" });
    return unwrapApiData(data);
  },
};
