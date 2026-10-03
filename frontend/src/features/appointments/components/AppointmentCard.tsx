import { memo } from "react";
import { Link } from "react-router-dom";

import { Avatar, Button } from "@/design-system";
import { AppointmentStatusBadge } from "@/features/appointments/components/AppointmentStatusBadge";
import type { Appointment } from "@/types/appointment";
import { formatDisplayDateTime } from "@/utils/date";

interface AppointmentCardProps {
  appointment: Appointment;
  onConfirm?: (appointment: Appointment) => void;
  onStart?: (appointment: Appointment) => void;
  compact?: boolean;
}

function AppointmentCardComponent({ appointment, onConfirm, onStart, compact }: AppointmentCardProps) {
  const time = formatDisplayDateTime(appointment.scheduled_at);

  if (compact) {
    return (
      <div className="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50/80 p-3 transition hover:border-primary-200 hover:bg-white">
        <Avatar name={appointment.patient.full_name} size="sm" />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-slate-900">{appointment.patient.full_name}</p>
          <p className="text-xs text-slate-500">{time}</p>
        </div>
        <AppointmentStatusBadge status={appointment.status} />
      </div>
    );
  }

  return (
    <article className="group rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm transition hover:border-primary-200 hover:shadow-md">
      <div className="flex items-start gap-4">
        <Avatar name={appointment.patient.full_name} size="md" />
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="font-semibold text-slate-900 group-hover:text-primary-700">
                {appointment.patient.full_name}
              </h3>
              <p className="text-xs font-mono text-slate-500">{appointment.appointment_number}</p>
            </div>
            <AppointmentStatusBadge status={appointment.status} />
          </div>

          <dl className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div>
              <dt className="text-slate-400">Horário</dt>
              <dd className="font-medium text-slate-700">{time}</dd>
            </div>
            <div>
              <dt className="text-slate-400">Médico</dt>
              <dd className="font-medium text-slate-700">{appointment.doctor?.full_name ?? "—"}</dd>
            </div>
          </dl>

          {appointment.chief_complaint && (
            <p className="mt-2 line-clamp-2 text-xs text-slate-500">{appointment.chief_complaint}</p>
          )}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
        <Link to={`/appointments/${appointment.id}`}>
          <Button size="sm" variant="outline">
            Detalhes
          </Button>
        </Link>
        {appointment.status === "EM_CONSULTA" && (
          <Link to={`/consultations/${appointment.id}`}>
            <Button size="sm" variant="primary">
              Prontuário
            </Button>
          </Link>
        )}
        {appointment.status === "AGENDADA" && onConfirm && (
          <Button size="sm" variant="secondary" onClick={() => onConfirm(appointment)}>
            Confirmar
          </Button>
        )}
        {(appointment.status === "CONFIRMADA" || appointment.status === "EM_ESPERA") && onStart && (
          <Button size="sm" variant="primary" onClick={() => onStart(appointment)}>
            Iniciar
          </Button>
        )}
      </div>
    </article>
  );
}

export const AppointmentCard = memo(AppointmentCardComponent);
