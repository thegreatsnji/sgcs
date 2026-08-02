import { Link } from "react-router-dom";

import { Badge, Card, ErrorState, LoadingState } from "@/design-system";
import { QUEUE_PRIORITY_LABELS, QUEUE_STATUS_LABELS } from "@/constants/reception";
import { ReceptionActivityFeed } from "@/features/reception/components/ReceptionActivityFeed";
import { ReceptionSubNav } from "@/features/reception/components/ReceptionSubNav";
import { useReceptionDashboard } from "@/features/reception/hooks/useReceptionDashboard";
import type { QueuePriority } from "@/types/reception";

export function ReceptionDashboardPage() {
  const { data, isLoading, isError, refetch } = useReceptionDashboard();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Receção</h2>
        <p className="mt-1 text-slate-600">Painel de receção — fila, entradas e indicadores.</p>
      </div>

      <ReceptionSubNav />

      {isLoading || !data ? (
        <LoadingState message="A carregar indicadores de receção..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar o painel de receção." onRetry={() => void refetch()} />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "Pacientes em espera", value: data.cards.patients_waiting },
              { label: "Tempo médio de espera", value: `${data.cards.average_wait_minutes} min` },
              { label: "Atendidos hoje", value: data.cards.attended_today },
              { label: "Emergências activas", value: data.cards.active_emergencies },
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
                  to="/reception/check-in"
                  className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
                >
                  Novo registo de entrada
                </Link>
                <Link
                  to="/reception/queue"
                  className="rounded-lg border border-primary-600 px-4 py-2 text-sm font-medium text-primary-700 hover:bg-primary-50"
                >
                  Ver fila
                </Link>
                <Link
                  to="/reception/referrals"
                  className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Encaminhamentos
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
                        <span className="font-medium text-slate-800">
                          #{entry.position} {entry.patient__full_name}
                        </span>
                        <p className="text-xs text-slate-500">{entry.patient__patient_number}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={entry.check_in__priority === "EMERGENCY" ? "danger" : "default"}>
                          {QUEUE_PRIORITY_LABELS[entry.check_in__priority as QueuePriority]}
                        </Badge>
                        <Badge>{QUEUE_STATUS_LABELS[entry.status as keyof typeof QUEUE_STATUS_LABELS] ?? entry.status}</Badge>
                      </div>
                    </li>
                  ))
                )}
              </ul>
            </Card>
          </div>

          <Card title="Actividade recente" description="Últimos movimentos na receção">
            <ReceptionActivityFeed items={data.recent_reception_activity} />
          </Card>
        </>
      )}
    </div>
  );
}
