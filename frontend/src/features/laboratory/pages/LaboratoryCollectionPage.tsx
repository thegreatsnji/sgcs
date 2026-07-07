import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ErrorState, LoadingState, useToast } from "@/design-system";
import { CollectionQueue } from "@/features/laboratory/components/CollectionQueue";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { laboratoryService } from "@/services/laboratory";
import { getApiErrorMessage } from "@/utils/api-error";

export function LaboratoryCollectionPage() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-collection"],
    queryFn: () => laboratoryService.getCollectionQueue(),
  });

  const collectMutation = useMutation({
    mutationFn: (id: number) => laboratoryService.collect(id),
    onSuccess: () => {
      showToast("Colheita registada.", "success");
      void queryClient.invalidateQueries({ queryKey: ["laboratory-collection"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-900">Fila de colheitas</h2>
      <LaboratorySubNav />
      {isLoading ? (
        <LoadingState message="A carregar fila..." />
      ) : isError ? (
        <ErrorState message="Erro ao carregar fila." onRetry={() => void refetch()} />
      ) : (
        <CollectionQueue
          orders={data?.results ?? []}
          onCollect={(o) => collectMutation.mutate(o.id)}
        />
      )}
    </div>
  );
}
