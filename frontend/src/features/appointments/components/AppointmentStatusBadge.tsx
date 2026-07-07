import { Badge } from "@/design-system";
import { APPOINTMENT_STATUS_LABELS, APPOINTMENT_STATUS_VARIANT } from "@/constants/appointments";
import type { Appointment, AppointmentStatus } from "@/types/appointment";

export function AppointmentStatusBadge({ status }: { status: AppointmentStatus }) {
  return (
    <Badge variant={APPOINTMENT_STATUS_VARIANT[status]}>{APPOINTMENT_STATUS_LABELS[status]}</Badge>
  );
}

export function AppointmentPatientCell({ appointment }: { appointment: Appointment }) {
  return (
    <div>
      <p className="font-medium text-slate-900">{appointment.patient.full_name}</p>
      <p className="text-xs text-slate-500">
        {appointment.appointment_number} — {appointment.patient.patient_number}
      </p>
    </div>
  );
}
