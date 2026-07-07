import { useQuery } from "@tanstack/react-query";

import { Card, ErrorState, LoadingState } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { TabelaResultados } from "@/features/laboratory/results/components/TabelaResultados";
import { laboratoryResultsService, laboratoryService } from "@/services/laboratory";

export function ResultsDashboardPage() {
  const { data: dashboard, isLoading: dashLoading } = useQuery({
    queryKey: ["laboratory-dashboard"],
    queryFn: laboratoryService.getDashboard,
  });

  const { data: results, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-results"],
    queryFn: () => laboratoryResultsService.list({ page: 1 }),
  });

  const kpis = dashboard?.resultados;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Resultados laboratoriais</h2>
        <p className="mt-1 text-slate-600">Gestão e validação de resultados de exames.</p>
      </div>
      <LaboratorySubNav />

      {!dashLoading && kpis && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Pendentes", value: kpis.resultados_pendentes },
            { label: "Validados", value: kpis.resultados_validados },
            { label: "Entregues hoje", value: kpis.resultados_entregues_hoje },
            { label: "Tempo médio (min)", value: kpis.tempo_medio_validacao_minutos },
          ].map((card) => (
            <Card key={card.label} title={card.label}>
              <p className="text-3xl font-bold text-primary-700">{card.value}</p>
            </Card>
          ))}
        </div>
      )}

      {isLoading || !results ? (
        <LoadingState message="A carregar resultados..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar resultados." onRetry={() => void refetch()} />
      ) : (
        <Card title="Resultados recentes">
          <TabelaResultados resultados={results.results} />
        </Card>
      )}
    </div>
  );
}
