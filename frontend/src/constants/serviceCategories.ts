/** Categorias de serviço (espelho de billing.constants.SERVICE_CATEGORIES) */
export const SERVICE_CATEGORY_OPTIONS = [
  { value: "CONSULTA", label: "Consulta" },
  { value: "LABORATORIO", label: "Laboratório" },
  { value: "ECOGRAFIA", label: "Ecografia" },
  { value: "ENFERMAGEM", label: "Enfermagem" },
  { value: "PROCEDIMENTO", label: "Procedimento" },
  { value: "CIRURGIA", label: "Cirurgia" },
  { value: "MATERNIDADE", label: "Maternidade" },
  { value: "MED_URGENCIA", label: "Medicamento de Urgência" },
  { value: "MATERIAL_CLINICO", label: "Material Clínico" },
  { value: "IMUNIZACAO", label: "Imunização" },
  { value: "DOCUMENTO", label: "Documento" },
  { value: "CARTAO", label: "Cartão" },
  { value: "OBSERVACAO_CLINICA", label: "Observação Clínica" },
  { value: "OUTRO", label: "Outro" },
] as const;

export function categoryLabel(code: string): string {
  return SERVICE_CATEGORY_OPTIONS.find((c) => c.value === code)?.label ?? code;
}
