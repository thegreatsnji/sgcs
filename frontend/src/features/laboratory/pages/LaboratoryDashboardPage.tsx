import { useQuery } from "@tanstack/react-query";

import { KpiCard } from "@/components/ui/KpiCard";
import { Card, ErrorState } from "@/design-system";
import { LaboratoryCard } from "@/features/laboratory/components/LaboratoryCard";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { LaboratoryDashboardSkeleton } from "@/features/laboratory/components/LaboratorySkeleton";
import { laboratoryService } from "@/services/laboratory";

export function LaboratoryDashboardPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-dashboard"],
    queryFn: laboratoryService.getDashboard,
    refetchInterval: 30_000,
  });

  const { data: pending } = useQuery({
    queryKey: ["laboratory-pending-preview"],
    queryFn: () => laboratoryService.getPending({ page: 1 }),
  });

  const { data: today } = useQuery({
    queryKey: ["laboratory-today"],
    queryFn: () => laboratoryService.getToday(),
  });

  if (isLoading || !data) return <LaboratoryDashboardSkeleton />;
  if (isError) return <ErrorState message="Não foi possível carregar o painel." onRetry={() => void refetch()} />;

  const todayCount = today?.results?.length ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Laboratório Diagnóstico</h1>
        <p className="mt-1 text-slate-500">Gestão de amostras, processamento e resultados analíticos.</p>
      </div>

      <LaboratorySubNav />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <KpiCard
          label="Amostras Hoje"
          value={todayCount}
          badge={{ text: "Pedidos do dia", variant: "info" }}
        />
        <KpiCard
          label="Pendentes"
          value={data.indicadores.pedidos_pendentes}
          badge={{ text: "Na fila", variant: "warning" }}
        />
        <KpiCard
          label="Em Processamento"
          value={data.indicadores.em_processamento}
          badge={{ text: "Activos", variant: "info" }}
        />
        <KpiCard
          label="Concluídos"
          value={data.indicadores.concluidos_hoje}
          badge={{ text: "Hoje", variant: "success" }}
        />
        <KpiCard
          label="Tempo de Resposta"
          value={`${data.indicadores.tempo_medio_minutos} min`}
          badge={{ text: "Tempo médio de resposta", variant: "default" }}
        />
      </div>

      {data.resultados && (
        <div>
          <h2 className="mb-4 text-lg font-semibold text-slate-900">Indicadores de resultados</h2>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard label="Resultados Pendentes" value={data.resultados.resultados_pendentes} badge={{ text: "Validação", variant: "warning" }} />
            <KpiCard label="Validados" value={data.resultados.resultados_validados} badge={{ text: "Prontos", variant: "success" }} />
            <KpiCard label="Entregues Hoje" value={data.resultados.resultados_entregues_hoje} badge={{ text: "Médicos", variant: "info" }} />
            <KpiCard label="Tempo de validação" value={`${data.resultados.tempo_medio_validacao_minutos} min`} badge={{ text: "Médio", variant: "default" }} />
          </div>
        </div>
      )}

      <Card title="Pedidos pendentes recentes">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {(pending?.results ?? []).length === 0 ? (
            <p className="col-span-full py-8 text-center text-sm text-slate-500">Sem pedidos pendentes.</p>
          ) : (
            (pending?.results ?? []).slice(0, 6).map((order) => (
              <LaboratoryCard key={order.id} order={order} />
            ))
          )}
        </div>
      </Card>
    </div>
  );
}
