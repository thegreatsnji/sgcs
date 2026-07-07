import { useQuery } from "@tanstack/react-query";

import { ErrorState, LoadingState } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { LaboratoryTable } from "@/features/laboratory/components/LaboratoryTable";
import { laboratoryService } from "@/services/laboratory";

export function LaboratoryTodayPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-today"],
    queryFn: () => laboratoryService.getToday(),
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-900">Pedidos do dia</h2>
      <LaboratorySubNav />
      {isLoading ? (
        <LoadingState message="A carregar pedidos do dia..." />
      ) : isError ? (
        <ErrorState message="Erro ao carregar pedidos." onRetry={() => void refetch()} />
      ) : (
        <LaboratoryTable orders={data?.results ?? []} />
      )}
    </div>
  );
}
