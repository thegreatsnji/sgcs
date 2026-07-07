import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ErrorState, LoadingState, useToast } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { LaboratoryTable } from "@/features/laboratory/components/LaboratoryTable";
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
      <h2 className="text-2xl font-bold text-slate-900">Pedidos pendentes</h2>
      <LaboratorySubNav />
      {isLoading ? (
        <LoadingState message="A carregar pedidos..." />
      ) : isError ? (
        <ErrorState message="Erro ao carregar pedidos." onRetry={() => void refetch()} />
      ) : (
        <LaboratoryTable
          orders={data?.results ?? []}
          onReceive={(o) => receiveMutation.mutate(o.id)}
        />
      )}
    </div>
  );
}
