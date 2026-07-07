import { useQuery } from "@tanstack/react-query";

import { Card, ErrorState, LoadingState } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { TabelaResultados } from "@/features/laboratory/results/components/TabelaResultados";
import { laboratoryResultsService } from "@/services/laboratory";

export function ResultHistoryPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-results-history"],
    queryFn: () => laboratoryResultsService.list({ page: 1, page_size: 50 }),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Histórico de resultados</h2>
        <p className="mt-1 text-slate-600">Todos os resultados laboratoriais registados.</p>
      </div>
      <LaboratorySubNav />

      {isLoading || !data ? (
        <LoadingState message="A carregar histórico..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar o histórico." onRetry={() => void refetch()} />
      ) : (
        <Card title="Resultados">
          <TabelaResultados resultados={data.results} emptyMessage="Nenhum resultado registado." />
        </Card>
      )}
    </div>
  );
}
