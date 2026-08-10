import { Link } from "react-router-dom";

import { PageHeader } from "@/components/layout/PageHeader";
import { KpiCard } from "@/components/ui/KpiCard";
import { UI_COPY } from "@/constants/uiCopy";
import { Button, ErrorState, SkeletonCard } from "@/design-system";
import { ReceptionQueueNowCard } from "@/features/reception/components/ReceptionQueueNowCard";
import { useReceptionDashboard } from "@/features/reception/hooks/useReceptionDashboard";

export function ReceptionRoleDashboardPage() {
  const { data, isLoading, isError, refetch } = useReceptionDashboard();

  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        message={UI_COPY.states.loadErrorReception}
        onRetry={() => void refetch()}
      />
    );
  }

  const waiting = data.cards.patients_waiting;
  const copy = UI_COPY.reception;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <PageHeader
        title={copy.dashboardTitle}
        actions={
          <Link to="/reception/atendimento?passo=1">
            <Button type="button">{copy.startAtendimento}</Button>
          </Link>
        }
      />

      <div className="grid gap-4 sm:grid-cols-3">
        <KpiCard label={copy.kpiWaiting} value={waiting} />
        <KpiCard
          label={copy.kpiAvgWait}
          value={
            waiting > 0 && data.cards.average_wait_minutes > 0
              ? `${data.cards.average_wait_minutes} min`
              : "—"
          }
        />
        <KpiCard label={copy.kpiAttendedToday} value={data.cards.attended_today} />
      </div>

      {data.cards.active_emergencies > 0 && (
        <div
          role="alert"
          className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 dark:border-red-900/50 dark:bg-red-950/40"
        >
          <p className="text-sm font-medium text-red-800 dark:text-red-300">
            {data.cards.active_emergencies}{" "}
            {data.cards.active_emergencies === 1 ? copy.emergencyInQueue : "Emergências na fila"}
          </p>
          <Link
            to="/reception/atendimento?passo=3"
            className="mt-1 inline-block text-sm font-medium text-red-700 hover:underline dark:text-red-300"
          >
            Abrir atendimento
          </Link>
        </div>
      )}

      <ReceptionQueueNowCard entries={data.queue_preview} />
    </div>
  );
}
