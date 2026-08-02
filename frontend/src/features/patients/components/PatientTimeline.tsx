import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { LoadingState } from "@/design-system";
import { patientsService } from "@/services/patients";
import { formatDisplayDateTime } from "@/utils/date";

interface PatientTimelineProps {
  patientId: number;
}

export function PatientTimeline({ patientId }: PatientTimelineProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["patient-history-timeline", patientId],
    queryFn: () => patientsService.listHistory(patientId, { page_size: 40 }),
  });

  if (isLoading) return <LoadingState message="A carregar linha temporal…" />;

  const entries = data?.results ?? [];

  if (entries.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-border px-4 py-8 text-center text-sm text-text-muted">
        Ainda não há eventos registados para este paciente.
      </p>
    );
  }

  return (
    <div className="relative">
      <div className="absolute top-0 bottom-0 left-[11px] w-px bg-border" aria-hidden />
      <ul className="space-y-6">
        {entries.map((entry) => (
          <li key={entry.id} className="relative pl-8">
            <span
              className="absolute left-0 top-1.5 h-[22px] w-[22px] rounded-full border-2 border-primary-500 bg-surface"
              aria-hidden
            />
            <div className="rounded-xl border border-border bg-surface p-4 shadow-sm transition hover:border-primary-200/80">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <p className="font-semibold text-text">{entry.title}</p>
                <time className="text-xs text-text-muted" dateTime={entry.event_date}>
                  {formatDisplayDateTime(entry.event_date)}
                </time>
              </div>
              {entry.description ? (
                <p className="mt-2 text-sm text-text-muted">{entry.description}</p>
              ) : null}
              <p className="mt-2 text-xs text-text-muted">
                {entry.source_module ? `Módulo: ${entry.source_module}` : null}
                {entry.recorded_by?.full_name ? ` · ${entry.recorded_by.full_name}` : null}
              </p>
            </div>
          </li>
        ))}
      </ul>
      <Link
        to={`/patients/${patientId}/history`}
        className="mt-4 inline-block text-sm font-semibold text-primary-600 hover:text-primary-700"
      >
        Ver histórico completo →
      </Link>
    </div>
  );
}
