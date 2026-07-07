import { api } from "@/services/api/client";
import type { ApiEnvelope, PaginatedResponse } from "@/types/api";
import type { CashRegister, Expense, FinanceDashboardData, FinanceMovement, FinanceReport } from "@/types/finance";
import { unwrapApiData } from "@/utils/api-response";

async function getPaginated<T>(url: string, params?: object) {
  const { data } = await api.get<ApiEnvelope<PaginatedResponse<T>>>(url, { params });
  return unwrapApiData(data);
}

export const financeService = {
  getDashboard: async () => {
    const { data } = await api.get<ApiEnvelope<FinanceDashboardData>>("/dashboard/finance/");
    return unwrapApiData(data);
  },
  listCashRegisters: async (params?: object) =>
    getPaginated<CashRegister>("/finance/cash-registers/", params),
  getCashRegister: async (id: number) => {
    const { data } = await api.get<ApiEnvelope<CashRegister>>(`/finance/cash-registers/${id}/`);
    return unwrapApiData(data);
  },
  openCashRegister: async (id: number, saldo_inicial: number) => {
    const { data } = await api.post<ApiEnvelope<CashRegister>>(`/finance/cash-registers/${id}/open/`, { saldo_inicial });
    return unwrapApiData(data);
  },
  closeCashRegister: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<CashRegister>>(`/finance/cash-registers/${id}/close/`);
    return unwrapApiData(data);
  },
  listMovements: async (params?: object) =>
    getPaginated<FinanceMovement>("/finance/movements/", params),
  listExpenses: async (params?: object) => getPaginated<Expense>("/finance/expenses/", params),
  createExpense: async (payload: object) => {
    const { data } = await api.post<ApiEnvelope<Expense>>("/finance/expenses/", payload);
    return unwrapApiData(data);
  },
  approveExpense: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<Expense>>(`/finance/expenses/${id}/approve/`);
    return unwrapApiData(data);
  },
  payExpense: async (id: number) => {
    const { data } = await api.post<ApiEnvelope<Expense>>(`/finance/expenses/${id}/pay/`);
    return unwrapApiData(data);
  },
  getDailyReport: async () => {
    const { data } = await api.get<ApiEnvelope<FinanceReport>>("/finance/reports/daily/");
    return unwrapApiData(data);
  },
  getMonthlyReport: async () => {
    const { data } = await api.get<ApiEnvelope<FinanceReport>>("/finance/reports/monthly/");
    return unwrapApiData(data);
  },
};
