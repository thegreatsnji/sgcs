import { memo, useMemo } from "react";

import { APPOINTMENT_STATUS_LABELS } from "@/constants/appointments";
import type { Appointment } from "@/types/appointment";

interface WeeklyAgendaGridProps {
  appointments: Appointment[];
  startDate: string;
  onSelect?: (appointment: Appointment) => void;
}

const WEEKDAY_LABELS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];

function WeeklyAgendaGridComponent({ appointments, startDate, onSelect }: WeeklyAgendaGridProps) {
  const days = useMemo(() => {
    const start = new Date(startDate);
    return Array.from({ length: 7 }, (_, i) => {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      const iso = d.toISOString().slice(0, 10);
      const dayAppointments = appointments.filter((a) => {
        const key = a.consultation_date ?? a.scheduled_at.slice(0, 10);
        return key === iso;
      });
      return {
        iso,
        label: WEEKDAY_LABELS[i] ?? d.toLocaleDateString("pt-PT", { weekday: "short" }),
        dateLabel: d.toLocaleDateString("pt-PT", { day: "numeric", month: "short" }),
        isToday: iso === new Date().toISOString().slice(0, 10),
        appointments: dayAppointments.sort(
          (a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime(),
        ),
      };
    });
  }, [appointments, startDate]);

  return (
    <div className="grid gap-3 lg:grid-cols-7">
      {days.map((day) => (
        <div
          key={day.iso}
          className={`min-h-[200px] rounded-2xl border p-3 ${
            day.isToday ? "border-primary-300 bg-primary-50/40" : "border-slate-200/80 bg-white"
          }`}
        >
          <div className="mb-3 border-b border-slate-100 pb-2">
            <p className={`text-xs font-bold uppercase ${day.isToday ? "text-primary-600" : "text-slate-500"}`}>
              {day.label}
            </p>
            <p className="text-sm font-semibold text-slate-900">{day.dateLabel}</p>
          </div>
          <div className="space-y-2">
            {day.appointments.length === 0 ? (
              <p className="text-[11px] text-slate-400">Sem consultas</p>
            ) : (
              day.appointments.map((a) => (
                <button
                  key={a.id}
                  type="button"
                  onClick={() => onSelect?.(a)}
                  className="w-full rounded-lg border border-slate-100 bg-slate-50/80 p-2 text-left transition hover:border-primary-200 hover:bg-white focus-ring"
                >
                  <p className="truncate text-[11px] font-semibold text-slate-900">
                    {new Date(a.scheduled_at).toLocaleTimeString("pt-PT", { hour: "2-digit", minute: "2-digit" })}
                  </p>
                  <p className="truncate text-[10px] text-slate-600">{a.patient.full_name}</p>
                  <p className="mt-1 truncate text-[9px] text-slate-400">
                    {APPOINTMENT_STATUS_LABELS[a.status]}
                  </p>
                </button>
              ))
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export const WeeklyAgendaGrid = memo(WeeklyAgendaGridComponent);
