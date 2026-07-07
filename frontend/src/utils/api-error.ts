import { isAxiosError } from "axios";

import type { ApiEnvelope } from "@/types/api";

export function getApiErrorMessage(error: unknown, fallback = "Ocorreu um erro inesperado."): string {
  if (isAxiosError<ApiEnvelope<unknown>>(error)) {
    const data = error.response?.data;
    if (data && typeof data === "object") {
      if ("message" in data && typeof data.message === "string" && data.message) {
        return data.message;
      }
      if ("errors" in data && data.errors) {
        if (typeof data.errors === "string") return data.errors;
        if (typeof data.errors === "object") {
          const first = Object.values(data.errors as Record<string, unknown>)[0];
          if (Array.isArray(first) && typeof first[0] === "string") return first[0];
          if (typeof first === "string") return first;
        }
      }
    }
    if (error.message) return error.message;
  }
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}
