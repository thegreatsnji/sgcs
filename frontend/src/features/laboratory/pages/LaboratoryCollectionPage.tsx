import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ErrorState, useToast } from "@/design-system";
import { CollectionQueue } from "@/features/laboratory/components/CollectionQueue";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { LaboratoryTableSkeleton } from "@/features/laboratory/components/LaboratorySkeleton";
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
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Fila de Colheitas</h1>
        <p className="mt-1 text-slate-500">Pacientes aguardando colheita de amostras biológicas.</p>
      </div>
      <LaboratorySubNav />
      {isLoading ? (
        <LaboratoryTableSkeleton rows={4} />
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
