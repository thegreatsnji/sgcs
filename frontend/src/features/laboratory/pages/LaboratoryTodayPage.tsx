import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ErrorState, useToast } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { LaboratoryTable } from "@/features/laboratory/components/LaboratoryTable";
import { LaboratoryTableSkeleton } from "@/features/laboratory/components/LaboratorySkeleton";
import { laboratoryService } from "@/services/laboratory";
import { getApiErrorMessage } from "@/utils/api-error";

export function LaboratoryTodayPage() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-today"],
    queryFn: () => laboratoryService.getToday(),
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["laboratory-today"] });
    void queryClient.invalidateQueries({ queryKey: ["laboratory-dashboard"] });
  };

  const startMutation = useMutation({
    mutationFn: (id: number) => laboratoryService.start(id),
    onSuccess: () => { showToast("Processamento iniciado.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const finishMutation = useMutation({
    mutationFn: (id: number) => laboratoryService.finish(id),
    onSuccess: () => { showToast("Pedido concluído.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const orders = data?.results ?? [];
  const inProcessing = orders.filter((o) => o.estado === "EM_PROCESSAMENTO");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Processamento</h1>
        <p className="mt-1 text-slate-500">
          Amostras do dia em análise — {inProcessing.length} em processamento de {orders.length} total.
        </p>
      </div>
      <LaboratorySubNav />
      {isLoading ? (
        <LaboratoryTableSkeleton />
      ) : isError ? (
        <ErrorState message="Erro ao carregar pedidos." onRetry={() => void refetch()} />
      ) : (
        <LaboratoryTable
          orders={orders}
          onStart={(o) => startMutation.mutate(o.id)}
          onFinish={(o) => finishMutation.mutate(o.id)}
          emptyTitle="Sem amostras hoje"
          emptyDescription="Não existem pedidos laboratoriais registados para hoje."
        />
      )}
    </div>
  );
}
