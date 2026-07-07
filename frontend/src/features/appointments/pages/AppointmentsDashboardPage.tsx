import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Card, ErrorState, LoadingState, useToast } from "@/design-system";
import { AppointmentCard } from "@/features/appointments/components/AppointmentCard";
import { AppointmentSubNav } from "@/features/appointments/components/AppointmentSubNav";
import { appointmentsService } from "@/services/appointments";
import { getApiErrorMessage } from "@/utils/api-error";

export function AppointmentsDashboardPage() {
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

  if (isLoading || !data) return <LoadingState message="A carregar agenda médica..." />;
  if (isError) return <ErrorState message="Erro ao carregar agenda." onRetry={() => void refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Agenda Médica</h2>
        <p className="mt-1 text-slate-600">Gestão de consultas — marcação, confirmação e acompanhamento.</p>
      </div>

      <AppointmentSubNav />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {[
          { label: "Consultas do dia", value: data.indicadores.consultas_do_dia },
          { label: "Concluídas", value: data.indicadores.consultas_concluidas },
          { label: "Em espera", value: data.indicadores.consultas_em_espera },
          { label: "Em consulta", value: data.indicadores.consultas_em_curso },
          { label: "Médicos activos", value: data.indicadores.medicos_em_servico },
        ].map((c) => (
          <Card key={c.label} title={c.label}>
            <p className="text-3xl font-bold text-primary-700">{c.value}</p>
          </Card>
        ))}
      </div>

      {data.proxima_consulta && (
        <Card title="Próxima consulta">
          <p className="font-medium text-slate-900">
            {data.proxima_consulta.patient} — {data.proxima_consulta.scheduled_at}
          </p>
          <Link to={`/appointments/${data.proxima_consulta.id}`} className="text-sm text-primary-700 hover:underline">
            Ver detalhes
          </Link>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {(today?.results ?? []).slice(0, 6).map((appointment) => (
          <AppointmentCard
            key={appointment.id}
            appointment={appointment}
            onConfirm={(a) => confirmMutation.mutate(a.id)}
          />
        ))}
      </div>
    </div>
  );
}
