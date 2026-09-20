import { api } from "@/services/api/client";
import type { ApiEnvelope } from "@/types/api";
import type { AdminDashboardData, ClinicalDashboardData } from "@/types/user-management";
import type { ConsultationDashboardData } from "@/types/appointment";
import type { ReceptionDashboardData } from "@/types/reception";
import { unwrapApiData } from "@/utils/api-response";

export type DirectorSection<T> =
  | { ok: true; data: T; error?: undefined }
  | { ok: false; error: string; data?: undefined };

export type DirectorDashboardData = {
  periodo: {
    data_inicio: string;
    data_fim: string;
    modo?: string;
  };
  financeiro: DirectorSection<{
    total_faturado: string;
    total_recebido: string;
    saldo_pendente: string;
    total_reducoes: string;
    numero_pagamentos: number;
    faturas_com_saldo: number;
  }>;
  operacional: DirectorSection<{
    utentes_atendidos: number;
    utentes_atendidos_definicao: string;
    consultas: number;
    consultas_concluidas: number;
    consultas_em_espera: number;
  }>;
  laboratorio: DirectorSection<{
    pedidos_pendentes: number;
    aguardam_regularizacao: number;
    aguardam_validacao: number;
    concluidos_periodo: number;
  }>;
  stock: DirectorSection<{
    stock_baixo: number;
    sem_stock: number;
    proximos_validade: number;
    expirados: number;
  }>;
  servicos_faturados: DirectorSection<{
    itens: Array<{ servico: string; quantidade: number }>;
    semantica: string;
  }>;
};

export type DirectorDashboardParams = {
  periodo: "hoje" | "semana" | "mes" | "personalizado";
  data_inicio?: string;
  data_fim?: string;
};

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

  getDirectorSummary: async (params: DirectorDashboardParams) => {
    const { data } = await api.get<ApiEnvelope<DirectorDashboardData>>("/dashboard/director/", {
      params,
    });
    return unwrapApiData(data);
  },
};
