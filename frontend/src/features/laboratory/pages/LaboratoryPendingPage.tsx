import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ErrorState, useToast } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { LaboratoryTable } from "@/features/laboratory/components/LaboratoryTable";
import { LaboratoryTableSkeleton } from "@/features/laboratory/components/LaboratorySkeleton";
import { laboratoryService } from "@/services/laboratory";
import { getApiErrorMessage } from "@/utils/api-error";

export function LaboratoryPendingPage() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-pending"],
    queryFn: () => laboratoryService.getPending(),
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["laboratory-pending"] });
    void queryClient.invalidateQueries({ queryKey: ["laboratory-dashboard"] });
  };

  const receiveMutation = useMutation({
    mutationFn: (id: number) => laboratoryService.receive(id),
    onSuccess: () => { showToast("Pedido recebido.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Pedidos Pendentes</h1>
        <p className="mt-1 text-slate-500">Pedidos aguardando receção no laboratório.</p>
      </div>
      <LaboratorySubNav />
      {isLoading ? (
        <LaboratoryTableSkeleton />
      ) : isError ? (
        <ErrorState message="Erro ao carregar pedidos." onRetry={() => void refetch()} />
      ) : (
        <LaboratoryTable
          orders={data?.results ?? []}
          onReceive={(o) => receiveMutation.mutate(o.id)}
          emptyTitle="Sem pedidos pendentes"
          emptyDescription="Todos os pedidos foram recebidos ou processados."
        />
      )}
    </div>
  );
}
