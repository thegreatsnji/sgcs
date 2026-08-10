export type VisitPurpose = "CONSULTA" | "CONTROLE";

export const VISIT_PURPOSE_LABELS: Record<VisitPurpose, string> = {
  CONSULTA: "Consulta (primeira vez ou novo problema)",
  CONTROLE: "Controlo (retorno / seguimento)",
};

/** Códigos do catálogo SauVida — alinhar com import do catálogo. */
export const VISIT_PURPOSE_SERVICE_CODIGO: Record<VisitPurpose, string> = {
  CONSULTA: "CONS-GERAL",
  CONTROLE: "CONS-CONTROLE",
};
