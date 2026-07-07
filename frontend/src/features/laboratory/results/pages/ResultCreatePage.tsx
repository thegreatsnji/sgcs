import { useMutation, useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { Button, LoadingState, useToast } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { ResultadoForm } from "@/features/laboratory/results/components/ResultadoForm";
import { laboratoryResultsService, laboratoryService } from "@/services/laboratory";
import { getApiErrorMessage } from "@/utils/api-error";

export function ResultCreatePage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [params] = useSearchParams();
  const pedidoId = Number(params.get("pedido"));

  const { data: pedido, isLoading } = useQuery({
    queryKey: ["laboratory-order", pedidoId],
    queryFn: () => laboratoryService.get(pedidoId),
    enabled: Number.isFinite(pedidoId),
  });

  const mutation = useMutation({
    mutationFn: laboratoryResultsService.create,
    onSuccess: (resultado) => {
      showToast("Resultado criado com sucesso.", "success");
      void navigate(`/laboratory/results/${resultado.id}`);
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (!Number.isFinite(pedidoId)) {
    return (
      <div className="space-y-6">
        <LaboratorySubNav />
        <ResultadoForm
          showPedidoField
          onSubmit={(values) => mutation.mutate(values)}
          isPending={mutation.isPending}
        />
      </div>
    );
  }

  if (isLoading || !pedido) return <LoadingState message="A carregar pedido..." />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Novo resultado</h2>
          <p className="text-slate-600">{pedido.numero_pedido} — {pedido.paciente.full_name}</p>
        </div>
        <Link to={`/laboratory/${pedido.id}`}>
          <Button variant="ghost">Voltar ao pedido</Button>
        </Link>
      </div>
      <LaboratorySubNav />
      <ResultadoForm
        initial={{ pedido_laboratorial: pedido.id }}
        pedidoLabel={`${pedido.numero_pedido} — ${pedido.paciente.full_name}`}
        onSubmit={(values) => mutation.mutate(values)}
        isPending={mutation.isPending}
      />
    </div>
  );
}
