import { api } from "@/services/api";

export interface UrgentMedicine {
  id: number;
  codigo: string;
  nome: string;
  forma_apresentacao: string;
  unidade: string;
  quantidade_stock: number;
  stock_minimo: number;
  servico: number | null;
  servico_codigo: string | null;
  activo: boolean;
  observacoes: string;
  abaixo_minimo: boolean;
}

export interface UrgentMedicineList {
  count: number;
  results: UrgentMedicine[];
}

export const pharmacyService = {
  listUrgentMedicines: async (params?: { search?: string; abaixo_minimo?: boolean }) => {
    const { data } = await api.get<{ data: UrgentMedicineList }>("/pharmacy/urgent-medicines/", {
      params: {
        search: params?.search,
        abaixo_minimo: params?.abaixo_minimo ? "1" : undefined,
        page_size: 200,
      },
    });
    return data.data;
  },

  registerMovement: async (
    id: number,
    payload: { tipo: "ENTRADA" | "SAIDA" | "AJUSTE"; quantidade: number; motivo?: string },
  ) => {
    const { data } = await api.post(`/pharmacy/urgent-medicines/${id}/movimento/`, payload);
    return data.data as { medicamento: UrgentMedicine };
  },
};
