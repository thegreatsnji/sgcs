import { useQuery } from "@tanstack/react-query";

import { Card, ErrorState } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { LaboratoryTableSkeleton } from "@/features/laboratory/components/LaboratorySkeleton";
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
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Histórico de Resultados</h1>
        <p className="mt-1 text-slate-500">Todos os resultados laboratoriais registados no sistema.</p>
      </div>
      <LaboratorySubNav />

      {isLoading || !data ? (
        <LaboratoryTableSkeleton rows={8} />
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
