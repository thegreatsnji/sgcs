/**
 * Referência clínica e validação de sinais vitais.
 * - Limites "duros" (domínio técnico): alinhados com CheckInCreateSerializer no backend.
 * - Limites "normais": só alertam — valores graves podem ser guardados após confirmação.
 */

export const VITAL_HARD_LIMITS = {
  temperature: { min: 30, max: 43 },
  spo2: { min: 0, max: 100 },
  heartRate: { min: 20, max: 250 },
  respiratoryRate: { min: 5, max: 80 },
  heightCm: { min: 30, max: 250 },
} as const;

export type VitalWarning = { field: string; message: string };

export function getVitalWarnings(input: {
  temperature?: number | null;
  blood_pressure?: string;
  spo2?: number | null;
  heart_rate?: number | null;
  respiratory_rate?: number | null;
}): VitalWarning[] {
  const warnings: VitalWarning[] = [];
  const t = input.temperature;
  if (t != null && Number.isFinite(t)) {
    if (t < 35) {
      warnings.push({
        field: "temperature",
        message: `Temperatura ${t} °C — muito baixa (hipotermia?). Confirme a medição.`,
      });
    } else if (t < 36.1 || t > 37.5) {
      warnings.push({
        field: "temperature",
        message: `Temperatura ${t} °C — fora do habitual (normal ~36–37 °C).`,
      });
    }
  }

  const spo2 = input.spo2;
  if (spo2 != null && Number.isFinite(spo2) && spo2 < 95) {
    warnings.push({
      field: "spo2",
      message: `SpO₂ ${spo2}% — baixa. Confirme oxímetro e paciente.`,
    });
  }

  const fc = input.heart_rate;
  if (fc != null && Number.isFinite(fc) && (fc < 60 || fc > 100)) {
    warnings.push({
      field: "heart_rate",
      message: `FC ${fc} b/min — fora do habitual (60–100).`,
    });
  }

  const fr = input.respiratory_rate;
  if (fr != null && Number.isFinite(fr) && (fr < 12 || fr > 20)) {
    warnings.push({
      field: "respiratory_rate",
      message: `FR ${fr} c/min — fora do habitual (12–20).`,
    });
  }

  const bp = input.blood_pressure?.trim() ?? "";
  const match = /^(\d{2,3})\/(\d{2,3})$/.exec(bp);
  if (match) {
    const sys = Number(match[1]);
    const dia = Number(match[2]);
    if (sys > 140 || sys < 90 || dia > 90 || dia < 60) {
      warnings.push({
        field: "blood_pressure",
        message: `TA ${bp} mmHg — fora do habitual. Confirme a medição.`,
      });
    }
  }

  return warnings;
}

/** Remove NaN/undefined de campos numéricos opcionais antes do POST. */
export function sanitizeOptionalNumber(value: number | undefined | null): number | undefined {
  if (value == null || Number.isNaN(value)) return undefined;
  return value;
}
