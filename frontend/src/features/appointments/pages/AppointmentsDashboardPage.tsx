import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";

import { IconCalendar } from "@/components/icons";
import { KpiCard } from "@/components/ui/KpiCard";
import { Card, ErrorState, useToast } from "@/design-system";
import { AppointmentCard } from "@/features/appointments/components/AppointmentCard";
import { AppointmentSubNav } from "@/features/appointments/components/AppointmentSubNav";
import { AppointmentsDashboardSkeleton } from "@/features/appointments/components/AppointmentsSkeleton";
import { DailyAgenda } from "@/features/appointments/components/DailyAgenda";
import { DoctorSchedulePanel } from "@/features/appointments/components/DoctorSchedulePanel";
import { appointmentsService } from "@/services/appointments";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDateTime } from "@/utils/date";

export function AppointmentsDashboardPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["consultas-dashboard"],
    queryFn: appointmentsService.getDashboard,
    refetchInterval: 30_000,
  });

  const { data: today } = useQuery({
    queryKey: ["appointments-today"],
    queryFn: () => appointmentsService.getToday(),
    refetchInterval: 30_000,
  });

  const confirmMutation = useMutation({
    mutationFn: (id: number) => appointmentsService.confirm(id),
    onSuccess: () => {
      showToast("Consulta confirmada.", "success");
      void queryClient.invalidateQueries({ queryKey: ["appointments-today"] });
      void queryClient.invalidateQueries({ queryKey: ["consultas-dashboard"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const startMutation = useMutation({
    mutationFn: (id: number) => appointmentsService.start(id),
    onSuccess: (_, id) => {
      showToast("Consulta iniciada.", "success");
      void queryClient.invalidateQueries({ queryKey: ["appointments-today"] });
      void queryClient.invalidateQueries({ queryKey: ["consultas-dashboard"] });
      navigate(`/consultations/${id}`);
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (isLoading || !data) return <AppointmentsDashboardSkeleton />;
  if (isError) return <ErrorState message="Erro ao carregar agenda." onRetry={() => void refetch()} />;

  const todayAppointments = today?.results ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Agenda Médica</h1>
        <p className="mt-1 text-slate-500">
          Marcação, confirmação e acompanhamento de consultas.
        </p>
      </div>

      <AppointmentSubNav />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          label="Consultas Hoje"
          value={data.indicadores.consultas_do_dia}
          icon={<IconCalendar />}
          badge={{ text: `${data.cards?.scheduled_today ?? data.indicadores.consultas_do_dia} agendadas`, variant: "info" }}
        />
        <KpiCard
          label="Em Espera"
          value={data.indicadores.consultas_em_espera}
          badge={{ text: "Sala de espera", variant: "warning" }}
        />
        <KpiCard
          label="Em Consulta"
          value={data.indicadores.consultas_em_curso}
          badge={{ text: "Activas agora", variant: "info" }}
        />
        <KpiCard
          label="Concluídas"
          value={data.indicadores.consultas_concluidas}
          badge={{ text: "Hoje", variant: "success" }}
        />
      </div>

      {data.proxima_consulta && (
        <Card className="border-primary-200 bg-gradient-to-r from-primary-50/50 to-white">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold tracking-wide text-primary-600 uppercase">Próxima consulta</p>
              <p className="mt-1 font-semibold text-slate-900">
                {data.proxima_consulta.patient}
              </p>
              <p className="text-sm text-slate-500">{formatDisplayDateTime(data.proxima_consulta.scheduled_at)}</p>
            </div>
            <button
              type="button"
              onClick={() => navigate(`/appointments/${data.proxima_consulta!.id}`)}
              className="rounded-xl bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-md shadow-primary-600/20 transition hover:bg-primary-700 focus-ring"
            >
              Ver detalhes
            </button>
          </div>
        </Card>
      )}

      <div className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2" title="Agenda do dia">
          <DailyAgenda
            appointments={todayAppointments}
            onSelect={(a) => navigate(`/appointments/${a.id}`)}
          />
        </Card>

        <Card title="Horário médico">
          <DoctorSchedulePanel />
        </Card>
      </div>

      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Consultas de hoje</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {todayAppointments.slice(0, 9).map((appointment) => (
            <AppointmentCard
              key={appointment.id}
              appointment={appointment}
              onConfirm={(a) => confirmMutation.mutate(a.id)}
              onStart={(a) => startMutation.mutate(a.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
