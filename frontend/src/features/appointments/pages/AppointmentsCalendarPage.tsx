import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { Card, Skeleton } from "@/design-system";
import { AppointmentCalendar } from "@/features/appointments/components/AppointmentCalendar";
import { AppointmentSubNav } from "@/features/appointments/components/AppointmentSubNav";
import { DailyAgenda } from "@/features/appointments/components/DailyAgenda";
import { DoctorSchedulePanel } from "@/features/appointments/components/DoctorSchedulePanel";
import { WeeklyAgendaGrid } from "@/features/appointments/components/WeeklyAgendaGrid";
import { appointmentsService } from "@/services/appointments";

type ViewMode = "week" | "day" | "list";

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function weekEndIso() {
  const d = new Date();
  d.setDate(d.getDate() + 6);
  return d.toISOString().slice(0, 10);
}

export function AppointmentsCalendarPage() {
  const navigate = useNavigate();
  const [view, setView] = useState<ViewMode>("week");

  const { data, isLoading } = useQuery({
    queryKey: ["appointments-calendar"],
    queryFn: () => appointmentsService.getCalendar({ start: todayIso(), end: weekEndIso() }),
  });

  const { data: today } = useQuery({
    queryKey: ["appointments-today"],
    queryFn: () => appointmentsService.getToday(),
  });

  const appointments = data ?? [];
  const todayAppointments = today?.results ?? [];

  const viewButton = (mode: ViewMode, label: string) => (
    <button
      type="button"
      onClick={() => setView(mode)}
      className={`rounded-xl px-4 py-2 text-sm font-medium transition focus-ring ${
        view === mode
          ? "bg-primary-600 text-white shadow-md shadow-primary-600/20"
          : "text-slate-600 hover:bg-slate-100"
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Calendário de Consultas</h1>
        <p className="mt-1 text-slate-500">Visão semanal, diária e horário médico.</p>
      </div>

      <AppointmentSubNav />

      <div className="flex flex-wrap gap-2">
        {viewButton("week", "Semana")}
        {viewButton("day", "Dia")}
        {viewButton("list", "Lista")}
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <Card>
            {isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full rounded-xl" />
                ))}
              </div>
            ) : view === "week" ? (
              <WeeklyAgendaGrid
                appointments={appointments}
                startDate={todayIso()}
                onSelect={(a) => navigate(`/appointments/${a.id}`)}
              />
            ) : view === "day" ? (
              <DailyAgenda
                appointments={todayAppointments}
                onSelect={(a) => navigate(`/appointments/${a.id}`)}
                title="Agenda de hoje"
              />
            ) : (
              <AppointmentCalendar
                appointments={appointments}
                onSelect={(a) => navigate(`/appointments/${a.id}`)}
              />
            )}
          </Card>
        </div>

        <Card title="Horário médico">
          <DoctorSchedulePanel />
        </Card>
      </div>
    </div>
  );
}
