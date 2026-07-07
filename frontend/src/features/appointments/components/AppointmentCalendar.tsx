import type { Appointment } from "@/types/appointment";
import { APPOINTMENT_STATUS_LABELS } from "@/constants/appointments";
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
      <div className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
        Sem consultas no período seleccionado.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {days.map((day) => (
        <div key={day}>
          <h3 className="mb-3 text-sm font-semibold text-slate-700">{day}</h3>
          <ul className="space-y-2">
            {grouped[day].map((appointment) => (
              <li key={appointment.id}>
                <button
                  type="button"
                  onClick={() => onSelect?.(appointment)}
                  className="flex w-full items-center justify-between rounded-lg border border-slate-200 px-4 py-3 text-left hover:bg-slate-50"
                >
                  <div>
                    <p className="font-medium text-slate-900">{appointment.patient.full_name}</p>
                    <p className="text-xs text-slate-500">{formatDisplayDateTime(appointment.scheduled_at)}</p>
                  </div>
                  <span className="text-xs text-slate-600">
                    {APPOINTMENT_STATUS_LABELS[appointment.status]}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
