import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { Card, LoadingState } from "@/design-system";
import { AppointmentCalendar } from "@/features/appointments/components/AppointmentCalendar";
import { AppointmentSubNav } from "@/features/appointments/components/AppointmentSubNav";
import { appointmentsService } from "@/services/appointments";

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function weekEndIso() {
  const d = new Date();
  d.setDate(d.getDate() + 7);
  return d.toISOString().slice(0, 10);
}

export function AppointmentsCalendarPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useQuery({
    queryKey: ["appointments-calendar"],
    queryFn: () => appointmentsService.getCalendar({ start: todayIso(), end: weekEndIso() }),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Calendário de Consultas</h2>
        <p className="mt-1 text-slate-600">Visão semanal das consultas agendadas.</p>
      </div>
      <AppointmentSubNav />
      <Card>
        {isLoading ? (
          <LoadingState message="A carregar calendário..." />
        ) : (
          <AppointmentCalendar
            appointments={data ?? []}
            onSelect={(a) => navigate(`/appointments/${a.id}`)}
          />
        )}
      </Card>
    </div>
  );
}
