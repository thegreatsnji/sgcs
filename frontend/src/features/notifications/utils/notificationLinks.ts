import type { Notificacao } from "@/types/notifications";

/** Deep link from notification metadata (lab result, patient, …). */
export function getNotificationHref(notificacao: Notificacao): string | null {
  const meta = notificacao.metadados;
  if (!meta || typeof meta !== "object") return null;

  const url = meta.url;
  if (typeof url === "string" && url.startsWith("/")) return url;

  const resultadoId = meta.resultado_id;
  if (typeof resultadoId === "number" || typeof resultadoId === "string") {
    return `/laboratory/results/${resultadoId}`;
  }

  const patientUrl = meta.patient_url;
  if (typeof patientUrl === "string" && patientUrl.startsWith("/")) return patientUrl;

  const patientId = meta.patient_id;
  if (typeof patientId === "number" || typeof patientId === "string") {
    return `/patients/${patientId}`;
  }

  return null;
}
