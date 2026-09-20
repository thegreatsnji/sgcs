import { isAxiosError } from "axios";

import type { ApiEnvelope } from "@/types/api";

const FIELD_LABELS: Record<string, string> = {
  spo2: "saturação de oxigénio (SpO₂)",
  heart_rate: "frequência cardíaca (FC)",
  respiratory_rate: "frequência respiratória (FR)",
  temperature: "temperatura",
  blood_pressure: "tensão arterial",
  weight: "peso",
  height_cm: "altura",
  age_at_check_in: "idade",
  symptoms: "queixas",
  triage_color: "cor de triagem",
  patient_id: "paciente",
  detail: "",
  non_field_errors: "",
};

function firstString(value: unknown): string | null {
  if (typeof value === "string" && value.trim()) return value.trim();
  if (Array.isArray(value) && typeof value[0] === "string" && value[0].trim()) {
    return value[0].trim();
  }
  return null;
}

/** Extrai erros por campo a partir de respostas DRF ou envelope SGCS. */
export function getApiFieldErrors(error: unknown): Record<string, string> {
  if (!isAxiosError(error) || !error.response?.data || typeof error.response.data !== "object") {
    return {};
  }
  const data = error.response.data as Record<string, unknown>;
  const source =
    data.errors && typeof data.errors === "object" && !Array.isArray(data.errors)
      ? (data.errors as Record<string, unknown>)
      : data;

  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(source)) {
    if (key === "success" || key === "message" || key === "data") continue;
    const msg = firstString(value);
    if (msg) out[key] = msg;
  }
  return out;
}

export function getApiErrorMessage(
  error: unknown,
  fallback = "Não foi possível concluir a operação. Tente novamente.",
): string {
  if (isAxiosError<ApiEnvelope<unknown> & Record<string, unknown>>(error)) {
    const data = error.response?.data;
    if (data && typeof data === "object") {
      if ("message" in data && typeof data.message === "string" && data.message.trim()) {
        // Prefer field detail when envelope message is generic
        const fields = getApiFieldErrors(error);
        const fieldKeys = Object.keys(fields).filter((k) => k !== "detail" && k !== "non_field_errors");
        if (fieldKeys.length === 1) return fields[fieldKeys[0]];
        if (fieldKeys.length > 1) {
          return "Não foi possível concluir a triagem. Verifique os campos assinalados.";
        }
        if (fields.detail) return fields.detail;
        if (fields.non_field_errors) return fields.non_field_errors;
        return data.message;
      }

      const fields = getApiFieldErrors(error);
      if (fields.detail) return fields.detail;
      if (fields.non_field_errors) return fields.non_field_errors;

      const fieldKeys = Object.keys(fields).filter((k) => k !== "detail" && k !== "non_field_errors");
      if (fieldKeys.length === 1) {
        const key = fieldKeys[0];
        const label = FIELD_LABELS[key];
        const msg = fields[key];
        if (label && !msg.toLowerCase().includes(label.split(" ")[0].toLowerCase())) {
          return `Verifique a ${label}. ${msg}`;
        }
        return msg;
      }
      if (fieldKeys.length > 1) {
        return "Não foi possível concluir a triagem. Verifique os campos assinalados.";
      }

      if ("errors" in data) {
        const err = firstString(data.errors);
        if (err) return err;
      }
    }

    // Never surface raw Axios status text to clinic staff
    if (error.response?.status && error.message?.startsWith("Request failed")) {
      return fallback;
    }
  }
  if (error instanceof Error && error.message && !error.message.startsWith("Request failed")) {
    return error.message;
  }
  return fallback;
}
