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
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Novo Resultado</h1>
          <p className="mt-1 text-slate-500">Registo de resultados analíticos.</p>
        </div>
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
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Registo de Resultado</h1>
          <p className="mt-1 text-slate-500">{pedido.numero_pedido} — entrada profissional de resultados</p>
        </div>
        <Link to={`/laboratory/${pedido.id}`}>
          <Button variant="ghost">Voltar ao pedido</Button>
        </Link>
      </div>
      <LaboratorySubNav />
      <ResultadoForm
        initial={{ pedido_laboratorial: pedido.id }}
        patientInfo={{
          full_name: pedido.paciente.full_name,
          patient_number: pedido.paciente.patient_number,
          numero_pedido: pedido.numero_pedido,
          medico_nome: pedido.medico?.full_name,
        }}
        onSubmit={(values) => mutation.mutate(values)}
        isPending={mutation.isPending}
      />
    </div>
  );
}
