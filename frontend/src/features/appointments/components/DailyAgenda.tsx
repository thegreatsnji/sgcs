import { memo } from "react";

import { Avatar } from "@/design-system";
import { APPOINTMENT_STATUS_LABELS } from "@/constants/appointments";
import type { Appointment } from "@/types/appointment";
import { formatDisplayDateTime } from "@/utils/date";

interface DailyAgendaProps {
  appointments: Appointment[];
  onSelect?: (appointment: Appointment) => void;
  title?: string;
}

function DailyAgendaComponent({ appointments, onSelect, title = "Agenda do dia" }: DailyAgendaProps) {
  const sorted = [...appointments].sort(
    (a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime(),
  );

  return (
    <div>
      <h3 className="mb-4 text-sm font-semibold text-slate-900">{title}</h3>
      {sorted.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-200 p-8 text-center text-sm text-slate-500">
          Sem consultas agendadas para este dia.
        </div>
      ) : (
        <div className="relative space-y-0">
          <div className="absolute top-2 bottom-2 left-[19px] w-px bg-slate-200" aria-hidden />
          {sorted.map((appointment) => (
            <button
              key={appointment.id}
              type="button"
              onClick={() => onSelect?.(appointment)}
              className="relative flex w-full gap-4 rounded-xl py-3 pr-3 pl-0 text-left transition hover:bg-slate-50 focus-ring"
            >
              <div className="relative z-10 mt-1 h-2.5 w-2.5 shrink-0 rounded-full border-2 border-primary-500 bg-white" />
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <time className="text-xs font-semibold text-primary-600">
                    {formatDisplayDateTime(appointment.scheduled_at)}
                  </time>
                  <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600">
                    {APPOINTMENT_STATUS_LABELS[appointment.status]}
                  </span>
                </div>
                <div className="mt-2 flex items-center gap-3">
                  <Avatar name={appointment.patient.full_name} size="sm" />
                  <div>
                    <p className="font-medium text-slate-900">{appointment.patient.full_name}</p>
                    <p className="text-xs text-slate-500">
                      {appointment.doctor?.full_name ?? "Sem médico"} · {appointment.appointment_number}
                    </p>
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export const DailyAgenda = memo(DailyAgendaComponent);
