import { Link } from "react-router-dom";

import { Button, Card } from "@/design-system";
import { AppointmentStatusBadge } from "@/features/appointments/components/AppointmentStatusBadge";
import type { Appointment } from "@/types/appointment";
import { formatDisplayDateTime } from "@/utils/date";

interface AppointmentCardProps {
  appointment: Appointment;
  onConfirm?: (appointment: Appointment) => void;
  onStart?: (appointment: Appointment) => void;
}

export function AppointmentCard({ appointment, onConfirm, onStart }: AppointmentCardProps) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-semibold text-slate-900">{appointment.patient.full_name}</p>
          <p className="text-xs text-slate-500">{appointment.appointment_number}</p>
          <p className="mt-2 text-sm text-slate-600">{formatDisplayDateTime(appointment.scheduled_at)}</p>
          <p className="text-sm text-slate-500">{appointment.doctor?.full_name ?? "Sem médico"}</p>
        </div>
        <AppointmentStatusBadge status={appointment.status} />
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Link to={`/appointments/${appointment.id}`}>
          <Button size="sm" variant="outline">
            Detalhes
          </Button>
        </Link>
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
    </Card>
  );
}
