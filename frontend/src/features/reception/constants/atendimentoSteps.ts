export const RECEPTION_ATENDIMENTO_STEPS = [
  { id: 1, label: "Paciente", short: "Utente" },
  { id: 2, label: "Triagem", short: "Triagem" },
  { id: 3, label: "Pagamento", short: "Pagar" },
  { id: 4, label: "Médico", short: "Médico" },
] as const;

export type ReceptionAtendimentoStepId = (typeof RECEPTION_ATENDIMENTO_STEPS)[number]["id"];

/** Ordem clínica SauVida: cobrar na receção antes de encaminhar para consulta. */
export function parseAtendimentoStep(raw: string | null): ReceptionAtendimentoStepId {
  const n = Number(raw);
  if (n === 5) return 4;
  if (n >= 1 && n <= 4) return n as ReceptionAtendimentoStepId;
  return 1;
}

export function buildAtendimentoUrl(params: {
  passo: ReceptionAtendimentoStepId;
  paciente?: number | null;
  queue?: number | null;
}): string {
  const sp = new URLSearchParams();
  sp.set("passo", String(params.passo));
  if (params.paciente) sp.set("paciente", String(params.paciente));
  if (params.queue) sp.set("fila", String(params.queue));
  return `/reception/atendimento?${sp.toString()}`;
}

export function encodeAtendimentoReturn(params: {
  passo: ReceptionAtendimentoStepId;
  paciente?: number | null;
  queue?: number | null;
}): string {
  return encodeURIComponent(buildAtendimentoUrl(params));
}
