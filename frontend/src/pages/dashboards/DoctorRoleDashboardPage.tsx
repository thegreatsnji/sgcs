import { Link, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { RoleDashboardHero } from "@/components/dashboards/RoleDashboardHero";
import { IconCalendar, IconPatients } from "@/components/icons";
import { KpiCard } from "@/components/ui/KpiCard";
import { Badge, Button, Card, ErrorState, SkeletonCard } from "@/design-system";
import { appointmentsService } from "@/services/appointments/appointments.service";
import { laboratoryService } from "@/services/laboratory";
import { APPOINTMENT_STATUS_LABELS } from "@/constants/appointments";
import { formatDisplayDateTime } from "@/utils/date";

export function DoctorRoleDashboardPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data, isLoading, isError, refetch, dataUpdatedAt, isFetching } = useQuery({
    queryKey: ["consultas-dashboard"],
    queryFn: appointmentsService.getDashboard,
    refetchInterval: 20_000,
  });

  const { data: lab } = useQuery({
    queryKey: ["laboratory-dashboard"],
    queryFn: laboratoryService.getDashboard,
    refetchInterval: 30_000,
  });

  const startMutation = useMutation({
    mutationFn: (id: number) => appointmentsService.start(id),
    onSuccess: (updated) => {
      void queryClient.invalidateQueries({ queryKey: ["consultas-dashboard"] });
      void queryClient.invalidateQueries({ queryKey: ["consultation-queue"] });
      navigate(`/consultations/${updated.id}`);
    },
    onError: (_error, id) => {
      navigate(`/consultations/${id}`);
    },
  });

  if (isLoading || !data) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (isError) {
    return <ErrorState message="Não foi possível carregar o painel médico." onRetry={() => void refetch()} />;
  }

  const indicadores = data.indicadores;
  const fila = data.queue_preview ?? [];

  return (
    <div className="space-y-6">
      <RoleDashboardHero
        tone="violet"
        eyebrow="Área clínica"
        title="Painel médico"
        description="Pacientes de hoje, fila e próximo atendimento."
        primaryAction={{ to: "/consultations/queue", label: "Fila de consultas" }}
        secondaryAction={{ to: "/consultations", label: "Registos clínicos" }}
        footer={
          dataUpdatedAt > 0
            ? isFetching
              ? "A actualizar…"
              : `Actualizado às ${new Date(dataUpdatedAt).toLocaleTimeString("pt-PT", { hour: "2-digit", minute: "2-digit" })}`
            : undefined
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          label="Pacientes hoje"
          value={indicadores.consultas_do_dia}
          badge={{ text: "Consultas agendadas", variant: "info" }}
          icon={<IconPatients />}
        />
        <KpiCard
          label="Em espera"
          value={indicadores.consultas_em_espera}
          badge={{ text: "Prontos para consulta", variant: "warning" }}
          icon={<IconPatients />}
        />
        <KpiCard
          label="Concluídas"
          value={indicadores.consultas_concluidas}
          badge={{ text: "Hoje", variant: "success" }}
          icon={<IconCalendar />}
        />
        <KpiCard
          label="Em consulta"
          value={indicadores.consultas_em_curso}
          badge={{ text: "Activas agora", variant: "info" }}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card
          className="lg:col-span-2"
          title="Próximo paciente"
          description="Atendimento imediato na fila"
        >
          {data.proxima_consulta ? (
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xl font-bold text-text">{data.proxima_consulta.patient}</p>
                <p className="text-sm text-text-muted">{data.proxima_consulta.appointment_number}</p>
                {data.proxima_consulta.doctor && (
                  <p className="mt-1 text-xs text-text-muted">Médico: {data.proxima_consulta.doctor}</p>
                )}
                <p className="mt-2 text-sm font-medium text-primary-600">
                  {formatDisplayDateTime(data.proxima_consulta.scheduled_at)}
                </p>
              </div>
              <Button
                variant="primary"
                disabled={startMutation.isPending}
                onClick={() => startMutation.mutate(data.proxima_consulta!.id)}
              >
                Atender agora
              </Button>
            </div>
          ) : (
            <p className="text-sm text-text-muted">Nenhum paciente na fila neste momento.</p>
          )}
        </Card>

        <Card title="Laboratório">
          <p className="text-3xl font-bold tabular-nums text-text">
            {lab?.resultados?.resultados_pendentes ?? 0}
          </p>
          <p className="mt-1 text-sm text-text-muted">Resultados pendentes de validação</p>
          <Link
            to="/laboratory/results"
            className="mt-4 inline-block text-sm font-semibold text-primary-600 hover:text-primary-700"
          >
            Ver resultados →
          </Link>
        </Card>
      </div>

      {fila.length > 0 && (
        <Card title="Consultas em espera" description={`${fila.length} na fila`}>
          <ul className="divide-y divide-border">
            {fila.slice(0, 8).map((item) => (
              <li key={item.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                <div>
                  <p className="font-medium text-text">{item.patient__full_name}</p>
                  <p className="text-xs text-text-muted">{item.patient__patient_number}</p>
                </div>
                <Badge variant="warning">
                  {APPOINTMENT_STATUS_LABELS[item.status as keyof typeof APPOINTMENT_STATUS_LABELS] ??
                    item.status}
                </Badge>
                <Link
                  to={`/consultations/${item.id}`}
                  className="text-sm font-semibold text-primary-600 hover:text-primary-700"
                >
                  Abrir
                </Link>
              </li>
            ))}
          </ul>
        </Card>
      )}

    </div>
  );
}
