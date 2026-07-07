import { useQuery } from "@tanstack/react-query";

import { Card, ErrorState, LoadingState } from "@/design-system";
import { LaboratoryCard } from "@/features/laboratory/components/LaboratoryCard";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Laboratório</h2>
        <p className="mt-1 text-slate-600">Gestão de pedidos laboratoriais.</p>
      </div>
      <LaboratorySubNav />

      {isLoading || !data ? (
        <LoadingState message="A carregar indicadores..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar o painel." onRetry={() => void refetch()} />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "Pendentes", value: data.indicadores.pedidos_pendentes },
              { label: "Em processamento", value: data.indicadores.em_processamento },
              { label: "Concluídos hoje", value: data.indicadores.concluidos_hoje },
              { label: "Tempo médio (min)", value: data.indicadores.tempo_medio_minutos },
            ].map((card) => (
              <Card key={card.label} title={card.label}>
                <p className="text-3xl font-bold text-primary-700">{card.value}</p>
              </Card>
            ))}
          </div>
          {data.resultados && (
            <div>
              <h3 className="mb-3 text-lg font-semibold text-slate-800">Indicadores de resultados</h3>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {[
                  { label: "Resultados pendentes", value: data.resultados.resultados_pendentes },
                  { label: "Resultados validados", value: data.resultados.resultados_validados },
                  { label: "Entregues hoje", value: data.resultados.resultados_entregues_hoje },
                  { label: "Tempo médio validação (min)", value: data.resultados.tempo_medio_validacao_minutos },
                ].map((card) => (
                  <Card key={card.label} title={card.label}>
                    <p className="text-2xl font-bold text-primary-700">{card.value}</p>
                  </Card>
                ))}
              </div>
            </div>
          )}
          <div>
            <h3 className="mb-3 text-lg font-semibold text-slate-800">Pedidos pendentes recentes</h3>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {(pending?.results ?? []).slice(0, 6).map((order) => (
                <LaboratoryCard key={order.id} order={order} />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
