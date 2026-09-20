import { Link } from "react-router-dom";

import { KpiCard } from "@/components/ui/KpiCard";
import { Badge, Card, EmptyState, ErrorState } from "@/design-system";
import { APPOINTMENT_STATUS_LABELS } from "@/constants/appointments";
import { ConsultationSubNav } from "@/features/appointments/components/ConsultationSubNav";
import { AppointmentsDashboardSkeleton } from "@/features/appointments/components/AppointmentsSkeleton";
import { useConsultationDashboard } from "@/features/appointments/hooks/useConsultationDashboard";
import type { AppointmentStatus } from "@/types/appointment";
import { formatDisplayDateTime } from "@/utils/date";

export function ConsultationDashboardPage() {
  const { data, isLoading, isError, refetch } = useConsultationDashboard();

  if (isLoading || !data) return <AppointmentsDashboardSkeleton />;
  if (isError) return <ErrorState message="Não foi possível carregar o painel." onRetry={() => void refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Consultas Médicas</h1>
        <p className="mt-1 text-slate-500">Fila, consultas activas e indicadores.</p>
      </div>

      <ConsultationSubNav />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          label="Em Espera"
          value={data.cards.waiting_for_doctor}
          badge={{ text: "Sala de espera", variant: "warning" }}
        />
        <KpiCard
          label="Em Consulta"
          value={data.cards.in_progress}
          badge={{ text: "Activas", variant: "info" }}
        />
        <KpiCard
          label="Concluídas Hoje"
          value={data.cards.completed_today}
          badge={{ text: "Hoje", variant: "success" }}
        />
        <KpiCard
          label="Agendadas Hoje"
          value={data.cards.scheduled_today}
          badge={{ text: "Restantes", variant: "default" }}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Acesso Rápido">
          <div className="flex flex-col gap-3 sm:flex-row">
            <Link to="/consultations/queue" className="flex-1">
              <button
                type="button"
                className="w-full rounded-xl bg-primary-600 px-4 py-3 text-sm font-semibold text-white shadow-md shadow-primary-600/20 transition hover:bg-primary-700"
              >
                Abrir fila médica
              </button>
            </Link>
            <Link to="/consultations/history" className="flex-1">
              <button
                type="button"
                className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              >
                Histórico
              </button>
            </Link>
          </div>
        </Card>

        <Card title="Pré-visualização da Fila">
          {data.queue_preview.length === 0 ? (
            <EmptyState title="Fila vazia" description="Nenhum paciente em espera." />
          ) : (
            <ul className="divide-y divide-slate-100">
              {data.queue_preview.map((entry) => (
                <li key={entry.id} className="flex items-center justify-between gap-3 py-3 first:pt-0">
                  <div className="min-w-0">
                    <p className="truncate font-medium text-slate-900">{entry.patient__full_name}</p>
                    <p className="text-xs text-slate-500">{entry.patient__patient_number}</p>
                  </div>
                  <div className="shrink-0 text-right">
                    <Badge>{APPOINTMENT_STATUS_LABELS[entry.status as AppointmentStatus]}</Badge>
                    <p className="mt-1 text-[11px] text-slate-400">
                      {formatDisplayDateTime(entry.scheduled_at)}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
