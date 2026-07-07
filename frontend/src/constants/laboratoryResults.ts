import type { ResultadoEstado } from "@/types/laboratoryResult";

export const RESULTADO_STATUS_LABELS: Record<ResultadoEstado, string> = {
  EM_PROCESSAMENTO: "Em processamento",
  RESULTADO_PENDENTE: "Resultado pendente",
  VALIDADO: "Validado",
  ENTREGUE: "Entregue",
};

export const RESULTADO_STATUS_VARIANT: Record<
  ResultadoEstado,
  "default" | "success" | "warning" | "danger" | "info"
> = {
  EM_PROCESSAMENTO: "info",
  RESULTADO_PENDENTE: "warning",
  VALIDADO: "success",
  ENTREGUE: "default",
};

export const INTERPRETACAO_LABELS: Record<string, string> = {
  NORMAL: "Normal",
  ALTO: "Alto",
  BAIXO: "Baixo",
  CRITICO: "Crítico",
};
