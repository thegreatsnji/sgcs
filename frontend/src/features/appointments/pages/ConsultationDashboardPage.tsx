import { Link } from "react-router-dom";

import { Badge, Card, ErrorState, LoadingState } from "@/design-system";
import { APPOINTMENT_STATUS_LABELS } from "@/constants/appointments";
import { ConsultationSubNav } from "@/features/appointments/components/ConsultationSubNav";
import { useConsultationDashboard } from "@/features/appointments/hooks/useConsultationDashboard";
import type { AppointmentStatus } from "@/types/appointment";
import { formatDisplayDateTime } from "@/utils/date";

export function ConsultationDashboardPage() {
  const { data, isLoading, isError, refetch } = useConsultationDashboard();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Consultas médicas</h2>
        <p className="mt-1 text-slate-600">Painel do médico — fila, consultas activas e indicadores.</p>
      </div>

      <ConsultationSubNav />

      {isLoading || !data ? (
        <LoadingState message="A carregar indicadores de consultas..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar o painel." onRetry={() => void refetch()} />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "À espera do médico", value: data.cards.waiting_for_doctor },
              { label: "Em curso", value: data.cards.in_progress },
              { label: "Concluídas hoje", value: data.cards.completed_today },
              { label: "Agendadas hoje", value: data.cards.scheduled_today },
              { label: "Pedidos lab. hoje", value: data.cards.lab_orders_today ?? data.indicadores.pedidos_laboratorio_emitidos ?? 0 },
              { label: "Pedidos img. hoje", value: data.cards.imaging_orders_today ?? data.indicadores.pedidos_imagiologia_emitidos ?? 0 },
            ].map((card) => (
              <Card key={card.label} title={card.label}>
                <p className="text-3xl font-bold text-primary-700">{card.value}</p>
              </Card>
            ))}
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card title="Acesso rápido">
              <div className="flex flex-wrap gap-3">
                <Link
                  to="/consultations/queue"
                  className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
                >
                  Fila médica
                </Link>
                <Link
                  to="/consultations/history"
                  className="rounded-lg border border-primary-600 px-4 py-2 text-sm font-medium text-primary-700 hover:bg-primary-50"
                >
                  Histórico
                </Link>
              </div>
            </Card>

            <Card title="Pré-visualização da fila">
              <ul className="space-y-3 text-sm">
                {data.queue_preview.length === 0 ? (
                  <li className="text-slate-500">Fila vazia.</li>
                ) : (
                  data.queue_preview.map((entry) => (
                    <li key={entry.id} className="flex items-center justify-between border-b border-slate-100 pb-2">
                      <div>
                        <span className="font-medium text-slate-800">{entry.patient__full_name}</span>
                        <p className="text-xs text-slate-500">{entry.patient__patient_number}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge>
                          {APPOINTMENT_STATUS_LABELS[entry.status as AppointmentStatus]}
                        </Badge>
                        <span className="text-xs text-slate-400">
                          {formatDisplayDateTime(entry.scheduled_at)}
                        </span>
                      </div>
                    </li>
                  ))
                )}
              </ul>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
