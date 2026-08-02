import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import {
  IconCalendar,
  IconPatients,
  IconSearch,
} from "@/components/icons";
import { KpiCard } from "@/components/ui/KpiCard";
import { QUEUE_PRIORITY_LABELS, QUEUE_STATUS_LABELS } from "@/constants/reception";
import { useReceptionDashboard } from "@/features/reception/hooks/useReceptionDashboard";
import { ReceptionActivityFeed } from "@/features/reception/components/ReceptionActivityFeed";
import { formatReceptionActivityTime } from "@/features/reception/utils/formatReceptionActivity";
import { Badge, Card, EmptyState, ErrorState, SkeletonCard } from "@/design-system";
import { appointmentsService } from "@/services/appointments/appointments.service";
import type { QueuePriority, QueueStatus } from "@/types/reception";

type QuickAction = {
  to: string;
  label: string;
  description: string;
  icon: typeof IconPatients;
  primary?: boolean;
};

const QUICK_ACTIONS: QuickAction[] = [
  {
    to: "/reception/atendimento",
    label: "Atendimento rápido",
    description: "Fluxo completo: paciente → fatura → fila",
    primary: true,
    icon: IconPatients,
  },
  {
    to: "/reception/check-in",
    label: "Triagem",
    description: "Pesquisar, registar e classificar utente",
    primary: true,
    icon: IconPatients,
  },
  {
    to: "/reception/queue",
    label: "Fila de espera",
    description: "Gerir fila e prioridades",
    icon: IconPatients,
  },
  {
    to: "/patients/new",
    label: "Novo paciente",
    description: "Registar utente na clínica",
    icon: IconPatients,
  },
  {
    to: "/patients",
    label: "Pesquisar paciente",
    description: "Localizar por nome ou processo",
    icon: IconSearch,
  },
  {
    to: "/appointments",
    label: "Consultas do dia",
    description: "Agenda e marcações",
    icon: IconCalendar,
  },
  {
    to: "/reception/referrals",
    label: "Encaminhamentos",
    description: "Enviar para médico ou lab.",
    icon: IconCalendar,
  },
];

function priorityVariant(priority: QueuePriority): "danger" | "warning" | "info" | "default" {
  switch (priority) {
    case "EMERGENCY":
      return "danger";
    case "HIGH":
      return "warning";
    case "NORMAL":
      return "info";
    default:
      return "default";
  }
}

function statusVariant(status: string): "success" | "warning" | "info" | "default" {
  switch (status) {
    case "IN_SERVICE":
      return "success";
    case "CALLED":
      return "warning";
    case "WAITING":
      return "info";
    default:
      return "default";
  }
}

export function ReceptionRoleDashboardPage() {
  const { data, isLoading, isError, refetch, dataUpdatedAt, isFetching } = useReceptionDashboard();

  const appointments = useQuery({
    queryKey: ["consultas-dashboard-reception"],
    queryFn: appointmentsService.getDashboard,
    refetchInterval: 30_000,
  });

  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          <SkeletonCard />
          <div className="lg:col-span-2">
            <SkeletonCard />
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState message="Não foi possível carregar o painel de receção." onRetry={() => void refetch()} />
    );
  }

  const consultasHoje = appointments.data?.indicadores.consultas_do_dia ?? 0;
  const proximaConsulta = appointments.data?.proxima_consulta;

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-emerald-500/25 bg-gradient-to-br from-emerald-600 via-emerald-700 to-slate-900 p-6 text-white shadow-lg shadow-emerald-900/20 sm:p-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-semibold tracking-[0.2em] text-emerald-100 uppercase">Área de Recepção</p>
            <h1 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">Painel da Rececionista</h1>
            <p className="mt-2 max-w-xl text-sm text-emerald-50/90">
              Acompanhe a fila, os registos de entrada e as consultas do dia em tempo real.
            </p>
          </div>
          <div className="flex shrink-0 flex-wrap gap-2">
            <Link
              to="/reception"
              className="inline-flex items-center rounded-xl border border-white/25 bg-white/10 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-white/20 focus-ring"
            >
              Módulo receção
            </Link>
            <Link
              to="/reception/check-in"
              className="inline-flex items-center rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-emerald-800 shadow-sm transition hover:bg-emerald-50 focus-ring"
            >
              + Novo check-in
            </Link>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-text-muted">
        <span className="inline-flex items-center gap-2">
          <span
            className={`h-2 w-2 rounded-full ${isFetching ? "animate-pulse bg-amber-500" : "bg-emerald-500"}`}
            aria-hidden
          />
          {isFetching ? "A actualizar..." : "Dados em tempo real"}
        </span>
        {dataUpdatedAt > 0 && (
          <span>
            Última actualização:{" "}
            {new Date(dataUpdatedAt).toLocaleTimeString("pt-PT", { hour: "2-digit", minute: "2-digit" })}
          </span>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          label="Em espera"
          value={data.cards.patients_waiting}
          badge={{
            text: data.cards.patients_waiting > 0 ? "Fila activa" : "Sem fila",
            variant: data.cards.patients_waiting > 0 ? "warning" : "success",
          }}
          icon={<IconPatients />}
          trend="Pacientes aguardando atendimento"
        />
        <KpiCard
          label="Tempo médio"
          value={`${data.cards.average_wait_minutes} min`}
          badge={{ text: "Espera estimada", variant: "info" }}
          trend="Média da fila actual"
        />
        <KpiCard
          label="Atendidos hoje"
          value={data.cards.attended_today}
          badge={{ text: "Check-ins concluídos", variant: "success" }}
          icon={<IconCalendar />}
        />
        <KpiCard
          label="Consultas hoje"
          value={consultasHoje}
          badge={{
            text: appointments.data ? `${appointments.data.indicadores.consultas_concluidas} concluídas` : "Agenda",
            variant: "info",
          }}
          icon={<IconCalendar />}
        />
      </div>

      {data.cards.active_emergencies > 0 && (
        <div
          role="alert"
          className="flex items-center justify-between gap-4 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 dark:border-red-900/50 dark:bg-red-950/40"
        >
          <div>
            <p className="font-semibold text-red-800 dark:text-red-300">
              {data.cards.active_emergencies} emergência{data.cards.active_emergencies > 1 ? "s" : ""} na fila
            </p>
            <p className="mt-0.5 text-sm text-red-700/80 dark:text-red-400/90">
              Priorize o atendimento imediato destes pacientes.
            </p>
          </div>
          <Link
            to="/reception/queue"
            className="inline-flex items-center rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700 focus-ring"
          >
            Ver fila
          </Link>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Fila — coluna principal */}
        <Card
          className="lg:col-span-2"
          title="Fila de espera"
          description={`${data.queue_preview.length} paciente${data.queue_preview.length !== 1 ? "s" : ""} na fila`}
          footer={
            <Link
              to="/reception/queue"
              className="text-sm font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400"
            >
              Gerir fila completa →
            </Link>
          }
        >
          {data.queue_preview.length === 0 ? (
            <EmptyState
              title="Fila vazia"
              description="Não há pacientes em espera. Registe um novo check-in quando um utente chegar à clínica."
              icon={<IconPatients className="mx-auto h-10 w-10 opacity-40" />}
              action={
                <Link
                  to="/reception/check-in"
                  className="inline-flex items-center rounded-xl bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-700 focus-ring"
                >
                  Registar entrada
                </Link>
              }
            />
          ) : (
            <ul className="space-y-3">
              {data.queue_preview.map((entry) => (
                <li
                  key={entry.id}
                  className="flex items-center gap-4 rounded-xl border border-border bg-surface-muted/40 p-4 transition hover:border-primary-200/60 hover:bg-surface-muted dark:hover:border-primary-500/30"
                >
                  <div
                    className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-sm font-bold tabular-nums ${
                      entry.check_in__priority === "EMERGENCY"
                        ? "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300"
                        : "bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300"
                    }`}
                  >
                    #{entry.position}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-semibold text-text">{entry.patient__full_name}</p>
                    <p className="mt-0.5 text-xs text-text-muted">
                      {entry.patient__patient_number}
                      {entry.estimated_wait_minutes != null && (
                        <> · ~{entry.estimated_wait_minutes} min</>
                      )}
                    </p>
                  </div>
                  <div className="flex shrink-0 flex-col items-end gap-1.5 sm:flex-row sm:items-center">
                    <Badge variant={priorityVariant(entry.check_in__priority)}>
                      {QUEUE_PRIORITY_LABELS[entry.check_in__priority]}
                    </Badge>
                    <Badge variant={statusVariant(entry.status)}>
                      {QUEUE_STATUS_LABELS[entry.status as QueueStatus] ?? entry.status}
                    </Badge>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* Atalhos */}
        <div className="space-y-4">
          <Card title="Acções rápidas">
            <div className="grid gap-2">
              {QUICK_ACTIONS.map((action) => {
                const Icon = action.icon;
                return (
                  <Link
                    key={action.to}
                    to={action.to}
                    className={`group flex items-start gap-3 rounded-xl border p-3.5 transition focus-ring ${
                      action.primary
                        ? "border-emerald-200 bg-emerald-50 hover:border-emerald-300 hover:bg-emerald-100/80 dark:border-emerald-800 dark:bg-emerald-950/40 dark:hover:bg-emerald-950/60"
                        : "border-border bg-surface hover:border-primary-200 hover:bg-surface-muted dark:hover:border-primary-500/30"
                    }`}
                  >
                    <span
                      className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${
                        action.primary
                          ? "bg-emerald-600 text-white"
                          : "bg-surface-muted text-primary-600 dark:text-primary-400"
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                    </span>
                    <span className="min-w-0">
                      <span className="block text-sm font-semibold text-text group-hover:text-primary-700 dark:group-hover:text-primary-300">
                        {action.label}
                      </span>
                      <span className="mt-0.5 block text-xs text-text-muted">{action.description}</span>
                    </span>
                  </Link>
                );
              })}
            </div>
          </Card>

          <Card title="Próxima consulta">
            {proximaConsulta ? (
              <div className="space-y-3">
                <div>
                  <p className="font-semibold text-text">{proximaConsulta.patient}</p>
                  <p className="text-sm text-text-muted">{proximaConsulta.appointment_number}</p>
                  {proximaConsulta.doctor && (
                    <p className="mt-1 text-xs text-text-muted">Médico: {proximaConsulta.doctor}</p>
                  )}
                  <p className="mt-1 text-xs font-medium text-primary-600 dark:text-primary-400">
                    {formatReceptionActivityTime(proximaConsulta.scheduled_at)}
                  </p>
                </div>
                <Link
                  to={`/appointments/${proximaConsulta.id}`}
                  className="inline-flex w-full items-center justify-center rounded-xl border border-border bg-surface px-4 py-2 text-sm font-semibold text-text transition hover:bg-surface-muted focus-ring"
                >
                  Ver consulta
                </Link>
              </div>
            ) : (
              <p className="text-sm text-text-muted">Sem consultas agendadas iminentes.</p>
            )}
          </Card>
        </div>
      </div>

      <Card title="Actividade recente" description="Últimos movimentos na receção">
        <ReceptionActivityFeed items={data.recent_reception_activity} limit={8} />
      </Card>
    </div>
  );
}
