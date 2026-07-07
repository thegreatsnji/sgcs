/** Limites de referência para destaque de sinais vitais anormais. */

export function isAbnormalVital(
  field: string,
  value: number | null | undefined,
): boolean {
  if (value == null) return false;
  switch (field) {
    case "frequencia_cardiaca":
      return value < 60 || value > 100;
    case "frequencia_respiratoria":
      return value < 12 || value > 20;
    case "temperatura":
      return value < 36.1 || value > 37.5;
    case "saturacao_oxigenio":
      return value < 95;
    case "imc":
      return value < 18.5 || value > 30;
    default:
      return false;
  }
}

export function parseBloodPressure(pa: string): { systolic?: number; diastolic?: number } {
  const match = pa.match(/(\d+)\s*\/\s*(\d+)/);
  if (!match) return {};
  return { systolic: Number(match[1]), diastolic: Number(match[2]) };
}

export function isAbnormalBloodPressure(pa: string): boolean {
  const { systolic, diastolic } = parseBloodPressure(pa);
  if (!systolic || !diastolic) return false;
  return systolic > 140 || systolic < 90 || diastolic > 90 || diastolic < 60;
}

export const CLINICAL_TABS = [
  { id: "resumo", label: "Resumo" },
  { id: "vitais", label: "Sinais Vitais" },
  { id: "soap", label: "SOAP" },
  { id: "diagnosticos", label: "Diagnósticos" },
  { id: "laboratorio", label: "Laboratório" },
  { id: "resultados_laboratorio", label: "Resultados Laboratoriais" },
  { id: "imagiologia", label: "Imagiologia" },
  { id: "seguimento", label: "Seguimento" },
  { id: "historico", label: "Histórico" },
] as const;
