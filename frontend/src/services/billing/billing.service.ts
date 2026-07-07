import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type {
  BillingDashboardData,
  BillingService,
  Invoice,
  PatientFinancialHistory,
  Payment,
  Quote,
  Receipt,
} from "@/types/billing";
import { unwrapApiData } from "@/utils/api-response";

async function getPaginated<T>(url: string, params?: object) {
  const { data } = await api.get<ApiEnvelope<PaginatedResponse<T>>>(url, { params });
  return unwrapApiData(data);
}

async function getOne<T>(url: string) {
  const { data } = await api.get<ApiEnvelope<T>>(url);
  return unwrapApiData(data);
}

export const billingService = {
  listServices: async (params?: object) => getPaginated<BillingService>("/billing/services/", params),
  getService: async (id: number) => getOne<BillingService>(`/billing/services/${id}/`),
  createService: async (payload: object) => {
    const { data } = await api.post<ApiEnvelope<BillingService>>("/billing/services/", payload);
    return unwrapApiData(data);
  },
  updateService: async (id: number, payload: object) => {
    const { data } = await api.patch<ApiEnvelope<BillingService>>(`/billing/services/${id}/`, payload);
    return unwrapApiData(data);
  },

  listQuotes: async (params?: object) => getPaginated<Quote>("/billing/quotes/", params),
  getQuote: async (id: number) => getOne<Quote>(`/billing/quotes/${id}/`),
  createQuote: async (payload: object) => {
    const { data } = await api.post<ApiEnvelope<Quote>>("/billing/quotes/", payload);
    return unwrapApiData(data);
  },
  approveQuote: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<Quote>>(`/billing/quotes/${id}/approve/`);
    return unwrapApiData(data);
  },

  listInvoices: async (params?: object) => getPaginated<Invoice>("/billing/invoices/", params),
  getInvoice: async (id: number) => getOne<Invoice>(`/billing/invoices/${id}/`),
  createInvoice: async (payload: object) => {
    const { data } = await api.post<ApiEnvelope<Invoice>>("/billing/invoices/", payload);
    return unwrapApiData(data);
  },

  listPayments: async (params?: object) => getPaginated<Payment>("/billing/payments/", params),
  createPayment: async (payload: object) => {
    const { data } = await api.post<ApiEnvelope<Payment>>("/billing/payments/", payload);
    return unwrapApiData(data);
  },
  confirmPayment: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<Payment>>(`/billing/payments/${id}/confirm/`);
    return unwrapApiData(data);
  },

  listReceipts: async (params?: object) => getPaginated<Receipt>("/billing/receipts/", params),
  getReceipt: async (id: number) => getOne<Receipt>(`/billing/receipts/${id}/`),

  getPatientHistory: async (patientId: number) =>
    getOne<PatientFinancialHistory>(`/billing/patient-history/${patientId}/`),

  getDashboard: async () => {
    const { data } = await api.get<ApiEnvelope<BillingDashboardData>>("/dashboard/billing/");
    return unwrapApiData(data);
  },
};
