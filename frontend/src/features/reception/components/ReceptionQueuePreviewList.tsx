import { Link } from "react-router-dom";

import { TYPO } from "@/constants/typography";
import { UI_COPY } from "@/constants/uiCopy";
import { TRIAGE_COLOR_LABELS } from "@/constants/reception";
import { Button } from "@/design-system";
import { buildAtendimentoUrl } from "@/features/reception/constants/atendimentoSteps";
import { PriorityBadge } from "@/features/reception/components/PriorityBadge";
import { QueueStatusBadge } from "@/features/reception/components/QueueStatusBadge";
import { TriageBadge } from "@/features/reception/components/TriageBadge";
import { VISIT_PURPOSE_LABELS, type VisitPurpose } from "@/features/reception/constants/visitPurpose";
import type { QueuePriority, QueueStatus, TriageColor } from "@/types/reception";

export interface ReceptionQueuePreviewEntry {
  id: number;
  position: number;
  status: string;
  estimated_wait_minutes: number | null;
  patient__id: number;
  patient__full_name: string;
  patient__patient_number: string;
  check_in__priority: QueuePriority;
  check_in__triage_color?: string;
  check_in__visit_purpose?: string;
}

const TRIAGE_STRIPE: Record<TriageColor, string> = {
  GREEN: "bg-emerald-500",
  YELLOW: "bg-amber-400",
  RED: "bg-red-500",
};

function formatWait(minutes: number | null): string | null {
  if (minutes == null) return null;
  return `~${minutes} min`;
}

export function ReceptionQueuePreviewList({ entries }: { entries: ReceptionQueuePreviewEntry[] }) {
  const copy = UI_COPY.reception;

  return (
    <ul className="divide-y divide-border-subtle">
      {entries.map((entry) => {
        const triage =
          entry.check_in__triage_color &&
          (["GREEN", "YELLOW", "RED"] as const).includes(entry.check_in__triage_color as TriageColor)
            ? (entry.check_in__triage_color as TriageColor)
            : null;
        const visit =
          entry.check_in__visit_purpose === "CONSULTA" || entry.check_in__visit_purpose === "CONTROLE"
            ? (entry.check_in__visit_purpose as VisitPurpose)
            : null;
        const status = entry.status as QueueStatus;
        const wait = formatWait(entry.estimated_wait_minutes);
        const showPriority =
          entry.check_in__priority === "HIGH" || entry.check_in__priority === "EMERGENCY";

        return (
          <li key={entry.id} className="flex flex-col gap-3 py-4 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex min-w-0 gap-3">
              {triage ? (
                <div
                  className={`mt-1 w-1 shrink-0 rounded-full ${TRIAGE_STRIPE[triage]}`}
                  aria-hidden
                  title={TRIAGE_COLOR_LABELS[triage]}
                />
              ) : (
                <div className="mt-1 w-1 shrink-0 rounded-full bg-border" aria-hidden />
              )}
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
                  <span className={`${TYPO.meta} tabular-nums`}>#{entry.position}</span>
                  <p className={`truncate ${TYPO.cardTitle}`}>{entry.patient__full_name}</p>
                </div>
                <p className={`mt-0.5 font-mono ${TYPO.meta}`}>{entry.patient__patient_number}</p>
                <p className={`mt-1 ${TYPO.meta}`}>
                  {copy.waitLabel}: {wait ?? "—"}
                  {visit ? ` · ${VISIT_PURPOSE_LABELS[visit]}` : null}
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  {triage ? <TriageBadge color={triage} /> : null}
                  {showPriority ? <PriorityBadge priority={entry.check_in__priority} /> : null}
                  <QueueStatusBadge status={status} />
                </div>
              </div>
            </div>

            <div className="flex shrink-0 items-center gap-2 sm:flex-col sm:items-stretch">
              <Link
                to={buildAtendimentoUrl({
                  passo: 3,
                  paciente: entry.patient__id,
                  queue: entry.id,
                })}
                className="inline-flex"
              >
                <Button type="button" size="sm" className="w-full sm:w-auto">
                  {copy.continueAtendimento}
                </Button>
              </Link>
              <Link
                to={`/patients/${entry.patient__id}`}
                className={`text-center ${TYPO.meta} font-medium text-primary-600 hover:underline dark:text-primary-400`}
              >
                {copy.viewPatient}
              </Link>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
