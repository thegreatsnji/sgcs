import { Badge } from "@/design-system";
import { QUEUE_STATUS_LABELS } from "@/constants/reception";
import type { QueueStatus } from "@/types/reception";

const STATUS_STYLE: Record<
  QueueStatus,
  { variant: "default" | "info" | "warning" | "success" | "danger"; ring: string }
> = {
  WAITING: { variant: "info", ring: "ring-sky-200 dark:ring-sky-800" },
  CALLED: { variant: "warning", ring: "ring-amber-200 dark:ring-amber-800" },
  IN_SERVICE: { variant: "success", ring: "ring-emerald-200 dark:ring-emerald-800" },
  COMPLETED: { variant: "default", ring: "ring-slate-200 dark:ring-slate-700" },
  CANCELLED: { variant: "danger", ring: "ring-red-200 dark:ring-red-800" },
};

/** Estados operacionais visíveis na fila da receção (um estado = um rótulo). */
export const QUEUE_OPERATIONAL_LABELS: Record<string, string> = {
  WAITING: "Aguardando",
  CALLED: "Chamado",
  IN_SERVICE: "Na consulta",
  COMPLETED: "Concluído",
  CANCELLED: "Cancelado",
};

interface QueueStatusBadgeProps {
  status: QueueStatus;
  /** Inclui encaminhamento laboratorial quando metadata existir */
  inLaboratory?: boolean;
}

export function QueueStatusBadge({ status, inLaboratory }: QueueStatusBadgeProps) {
  const style = STATUS_STYLE[status];
  const label = inLaboratory
    ? "No laboratório"
    : QUEUE_OPERATIONAL_LABELS[status] ?? QUEUE_STATUS_LABELS[status];

  return (
    <span className={`inline-flex rounded-full ring-2 ring-inset ${style.ring}`}>
      <Badge variant={style.variant}>{label}</Badge>
    </span>
  );
}
