import { api } from "@/services/api";

export type StockCategory = "MEDICAMENTO" | "MATERIAL_CLINICO" | "TESTE_RAPIDO" | "OUTRO";
export type StockStatus =
  | "DISPONIVEL"
  | "STOCK_BAIXO"
  | "SEM_STOCK"
  | "EXPIRADO"
  | "PROXIMO_DA_VALIDADE";

export interface UrgentMedicine {
  id: number;
  codigo: string;
  nome: string;
  forma_apresentacao: string;
  categoria: StockCategory;
  unidade: string;
  quantidade_stock: number;
  stock_minimo: number;
  validade: string | null;
  preco_referencia_fcfa: string | null;
  quantidade_texto_original: string;
  servico: number | null;
  servico_codigo: string | null;
  activo: boolean;
  observacoes: string;
  abaixo_minimo: boolean;
  estado: StockStatus;
}

export interface StockMovement {
  id: number;
  medicamento: number;
  medicamento_nome: string;
  tipo: "ENTRADA" | "SAIDA" | "AJUSTE" | "PERDA_EXPIRACAO";
  quantidade: number;
  quantidade_antes: number;
  quantidade_depois: number;
  motivo: string;
  origem: string;
  operador: number | null;
  operador_nome: string;
  paciente: number | null;
  paciente_nome: string | null;
  created_at: string;
}

export interface UrgentMedicineList {
  count: number;
  results: UrgentMedicine[];
}

export interface StockDashboard {
  total_itens: number;
  stock_baixo: number;
  sem_stock: number;
  proximos_validade: number;
  expirados: number;
  precisa_atencao: UrgentMedicine[];
}

export const pharmacyService = {
  listUrgentMedicines: async (params?: {
    search?: string;
    abaixo_minimo?: boolean;
    categoria?: string;
    estado?: string;
  }) => {
    const { data } = await api.get<{ data: UrgentMedicineList }>("/stock/items/", {
      params: {
        search: params?.search,
        abaixo_minimo: params?.abaixo_minimo ? "1" : undefined,
        categoria: params?.categoria,
        estado: params?.estado,
        page_size: 200,
      },
    });
    return data.data;
  },

  createItem: async (payload: Record<string, unknown>) => {
    const { data } = await api.post("/stock/items/", payload);
    return data.data as UrgentMedicine;
  },

  registerMovement: async (
    id: number,
    payload: {
      tipo?: "ENTRADA" | "SAIDA" | "AJUSTE" | "PERDA_EXPIRACAO";
      quantidade: number;
      motivo?: string;
      paciente?: number;
    },
    kind: "entrada" | "saida" | "ajuste" | "movimento" = "movimento",
  ) => {
    const { data } = await api.post(`/stock/items/${id}/${kind}/`, payload);
    return data.data as { item: UrgentMedicine; medicamento: UrgentMedicine };
  },

  listMovements: async (params?: { medicamento?: number; tipo?: string }) => {
    const { data } = await api.get<{ data: { count: number; results: StockMovement[] } }>(
      "/stock/movements/",
      { params: { ...params, page_size: 100 } },
    );
    return data.data;
  },

  dashboard: async () => {
    const { data } = await api.get<{ data: StockDashboard }>("/stock/dashboard/");
    return data.data;
  },
};
