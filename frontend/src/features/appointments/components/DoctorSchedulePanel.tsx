import { useQuery } from "@tanstack/react-query";
import { memo } from "react";

import { Avatar, Badge, Skeleton } from "@/design-system";
import { APPOINTMENT_STATUS_LABELS } from "@/constants/appointments";
import { appointmentsService } from "@/services/appointments";
import { formatDisplayDateTime } from "@/utils/date";

interface DoctorSchedulePanelProps {
  date?: string;
}

function DoctorSchedulePanelComponent({ date }: DoctorSchedulePanelProps) {
  const scheduleDate = date ?? new Date().toISOString().slice(0, 10);

  const { data, isLoading } = useQuery({
    queryKey: ["appointments-doctor-schedule", scheduleDate],
    queryFn: () => appointmentsService.getDoctor({ date: scheduleDate }),
  });

  const appointments = data?.results ?? [];

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">Horário médico</h3>
        <Badge variant="info">{appointments.length} consultas</Badge>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full rounded-xl" />
          ))}
        </div>
      ) : appointments.length === 0 ? (
        <p className="rounded-xl border border-dashed border-slate-200 p-6 text-center text-sm text-slate-500">
          Sem consultas no horário médico para esta data.
        </p>
      ) : (
        <ul className="space-y-2">
          {appointments.map((appointment) => (
            <li
              key={appointment.id}
              className="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50/50 p-3"
            >
              <Avatar name={appointment.patient.full_name} size="sm" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-900">{appointment.patient.full_name}</p>
                <p className="text-xs text-slate-500">
                  {formatDisplayDateTime(appointment.scheduled_at)} · {appointment.doctor?.full_name ?? "—"}
                </p>
              </div>
              <Badge variant="default">{APPOINTMENT_STATUS_LABELS[appointment.status]}</Badge>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export const DoctorSchedulePanel = memo(DoctorSchedulePanelComponent);
