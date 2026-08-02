import type { Appointment } from "@/types/appointment";
import { APPOINTMENT_STATUS_LABELS } from "@/constants/appointments";
import { Avatar } from "@/design-system";
import { formatDisplayDateTime } from "@/utils/date";

interface AppointmentCalendarProps {
  appointments: Appointment[];
  onSelect?: (appointment: Appointment) => void;
}

export function AppointmentCalendar({ appointments, onSelect }: AppointmentCalendarProps) {
  const grouped = appointments.reduce<Record<string, Appointment[]>>((acc, item) => {
    const key = item.consultation_date ?? item.scheduled_at.slice(0, 10);
    acc[key] = acc[key] ? [...acc[key], item] : [item];
    return acc;
  }, {});

  const days = Object.keys(grouped).sort();

  if (days.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-200 p-10 text-center text-sm text-slate-500">
        Sem consultas no período seleccionado.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {days.map((day) => (
        <section key={day}>
          <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-slate-900">
            <span className="h-2 w-2 rounded-full bg-primary-500" aria-hidden />
            {new Date(day).toLocaleDateString("pt-PT", {
              weekday: "long",
              day: "numeric",
              month: "long",
            })}
          </h3>
          <ul className="space-y-2">
            {grouped[day]
              .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())
              .map((appointment) => (
                <li key={appointment.id}>
                  <button
                    type="button"
                    onClick={() => onSelect?.(appointment)}
                    className="flex w-full items-center gap-4 rounded-2xl border border-slate-200/80 px-4 py-3 text-left transition hover:border-primary-200 hover:bg-slate-50 focus-ring"
                  >
                    <Avatar name={appointment.patient.full_name} size="sm" />
                    <div className="min-w-0 flex-1">
                      <p className="font-medium text-slate-900">{appointment.patient.full_name}</p>
                      <p className="text-xs text-slate-500">
                        {formatDisplayDateTime(appointment.scheduled_at)} · {appointment.doctor?.full_name ?? "—"}
                      </p>
                    </div>
                    <span className="shrink-0 rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                      {APPOINTMENT_STATUS_LABELS[appointment.status]}
                    </span>
                  </button>
                </li>
              ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
