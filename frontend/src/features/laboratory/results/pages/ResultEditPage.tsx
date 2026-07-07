import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { Button, ErrorState, LoadingState, useToast } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { ResultadoForm } from "@/features/laboratory/results/components/ResultadoForm";
import { laboratoryResultsService } from "@/services/laboratory";
import { getApiErrorMessage } from "@/utils/api-error";

export function ResultEditPage() {
  const { id } = useParams<{ id: string }>();
  const resultId = Number(id);
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-result", resultId],
    queryFn: () => laboratoryResultsService.get(resultId),
    enabled: Number.isFinite(resultId),
  });

  const mutation = useMutation({
    mutationFn: (payload: { observacoes?: string; conclusao?: string }) =>
      laboratoryResultsService.update(resultId, payload),
    onSuccess: () => {
      showToast("Resultado actualizado.", "success");
      void queryClient.invalidateQueries({ queryKey: ["laboratory-result", resultId] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (!Number.isFinite(resultId)) return <ErrorState message="Resultado inválido." />;
  if (isLoading || !data) return <LoadingState message="A carregar resultado..." />;
  if (isError) return <ErrorState message="Erro ao carregar." onRetry={() => void refetch()} />;
  if (!data.editavel) {
    return (
      <div className="space-y-4">
        <ErrorState message="Este resultado já foi validado e não pode ser editado." />
        <Link to={`/laboratory/results/${resultId}`} className="text-sm text-primary-700 hover:underline">
          Ver detalhes do resultado
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-slate-900">Editar resultado</h2>
        <Link to={`/laboratory/results/${resultId}`}>
          <Button variant="ghost">Cancelar</Button>
        </Link>
      </div>
      <LaboratorySubNav />
      <ResultadoForm
        initial={{
          pedido_laboratorial: data.pedido_laboratorial,
          observacoes: data.observacoes,
          conclusao: data.conclusao,
          parametros: data.parametros,
        }}
        pedidoLabel={`${data.numero_pedido} — ${data.paciente_nome}`}
        onSubmit={(values) =>
          mutation.mutate({ observacoes: values.observacoes, conclusao: values.conclusao })
        }
        isPending={mutation.isPending}
      />
    </div>
  );
}
