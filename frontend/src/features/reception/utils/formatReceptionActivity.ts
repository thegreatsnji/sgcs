import { QUEUE_PRIORITY_LABELS, QUEUE_STATUS_LABELS, TRIAGE_COLOR_LABELS } from "@/constants/reception";
import type { QueuePriority, QueueStatus } from "@/types/reception";

export interface ReceptionActivityItem {
  action: string;
  description: string;
  user: string;
  created_at: string;
}

type ActivityTone = "emerald" | "sky" | "amber" | "violet" | "slate";

interface ActivityMeta {
  label: string;
  tone: ActivityTone;
}

const ACTION_META: Record<string, ActivityMeta> = {
  RECEPTION_CHECK_IN: { label: "Triagem", tone: "emerald" },
  RECEPTION_STATUS_CHANGE: { label: "Estado da fila", tone: "sky" },
  RECEPTION_ASSIGN_DOCTOR: { label: "Encaminhamento médico", tone: "violet" },
  RECEPTION_REFERRAL: { label: "Encaminhamento", tone: "amber" },
  RECEPTION_CANCEL: { label: "Cancelamento", tone: "slate" },
};

const STATUS_TOKENS = Object.entries(QUEUE_STATUS_LABELS).reduce(
  (acc, [key, label]) => {
    acc[key] = label;
    return acc;
  },
  {} as Record<string, string>,
);

const PRIORITY_TOKENS = Object.entries(QUEUE_PRIORITY_LABELS).reduce(
  (acc, [key, label]) => {
    acc[key] = label;
    return acc;
  },
  {} as Record<string, string>,
);

function replaceTokens(text: string): string {
  let result = text
    .replace(/Check-in/gi, "Triagem")
    .replace(/check-in/gi, "triagem")
    .replace(/Triagem do paciente/gi, "Triagem do paciente");

  for (const [token, label] of Object.entries(STATUS_TOKENS)) {
    result = result.replace(new RegExp(`\\b${token}\\b`, "g"), label);
  }
  for (const [token, label] of Object.entries(PRIORITY_TOKENS)) {
    result = result.replace(new RegExp(`\\b${token}\\b`, "g"), label);
  }
  for (const [token, label] of Object.entries(TRIAGE_COLOR_LABELS)) {
    result = result.replace(new RegExp(`\\b${token}\\b`, "g"), label);
  }

  return result.replace(/\s{2,}/g, " ").trim();
}

export function getReceptionActivityMeta(action: string): ActivityMeta {
  return ACTION_META[action] ?? { label: "Actividade", tone: "slate" };
}

export function formatReceptionActivityDescription(description: string): string {
  return replaceTokens(description);
}

export function formatReceptionActivityTime(value: string): string {
  const match = value.match(/^(\d{2})\/(\d{2})\/(\d{4}) (\d{2}):(\d{2})$/);
  const date = match
    ? new Date(
        Number(match[3]),
        Number(match[2]) - 1,
        Number(match[1]),
        Number(match[4]),
        Number(match[5]),
      )
    : new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  const now = new Date();
  const isToday =
    date.getDate() === now.getDate() &&
    date.getMonth() === now.getMonth() &&
    date.getFullYear() === now.getFullYear();

  const time = date.toLocaleTimeString("pt-PT", { hour: "2-digit", minute: "2-digit" });
  if (isToday) return `Hoje, ${time}`;

  return date.toLocaleString("pt-PT", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function getUserInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

export const ACTIVITY_TONE_CLASSES: Record<
  ActivityTone,
  { icon: string; badge: "success" | "info" | "warning" | "default" }
> = {
  emerald: { icon: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300", badge: "success" },
  sky: { icon: "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300", badge: "info" },
  amber: { icon: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300", badge: "warning" },
  violet: { icon: "bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300", badge: "info" },
  slate: { icon: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300", badge: "default" },
};

/** Extrai prioridade da descrição, se existir. */
export function extractPriorityFromDescription(description: string): QueuePriority | null {
  const match = description.match(/\b(LOW|NORMAL|HIGH|EMERGENCY)\b/);
  return match ? (match[1] as QueuePriority) : null;
}

/** Extrai estado da fila da descrição, se existir. */
export function extractStatusFromDescription(description: string): QueueStatus | null {
  const match = description.match(/\b(WAITING|CALLED|IN_SERVICE|COMPLETED|CANCELLED)\b/);
  return match ? (match[1] as QueueStatus) : null;
}
