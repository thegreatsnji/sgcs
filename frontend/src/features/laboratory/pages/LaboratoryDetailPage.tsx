import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { Button, Card, ErrorState, LoadingState, useToast } from "@/design-system";
import { PRIORITY_LABELS } from "@/constants/appointments";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { StatusBadge } from "@/features/laboratory/components/StatusBadge";
import { laboratoryService } from "@/services/laboratory";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDateTime } from "@/utils/date";

export function LaboratoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const orderId = Number(id);
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-order", orderId],
    queryFn: () => laboratoryService.get(orderId),
    enabled: Number.isFinite(orderId),
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["laboratory-order", orderId] });
    void queryClient.invalidateQueries({ queryKey: ["laboratory-pending"] });
    void queryClient.invalidateQueries({ queryKey: ["laboratory-dashboard"] });
  };

  const actionMutation = useMutation({
    mutationFn: async (action: "receive" | "collect" | "start" | "finish") => {
      if (action === "receive") return laboratoryService.receive(orderId);
      if (action === "collect") return laboratoryService.collect(orderId);
      if (action === "start") return laboratoryService.start(orderId);
      return laboratoryService.finish(orderId);
    },
    onSuccess: () => { showToast("Estado actualizado.", "success"); invalidate(); },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  if (!Number.isFinite(orderId)) return <ErrorState message="Pedido inválido." />;
  if (isLoading || !data) return <LoadingState message="A carregar pedido..." />;
  if (isError) return <ErrorState message="Erro ao carregar pedido." onRetry={() => void refetch()} />;

  const isFinal = data.estado === "CONCLUIDO" || data.estado === "CANCELADO";

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{data.numero_pedido}</h2>
          <p className="text-slate-600">{data.paciente.full_name}</p>
        </div>
        <StatusBadge status={data.estado} />
      </div>
      <LaboratorySubNav />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Informação">
          <dl className="space-y-2 text-sm">
            <div><dt className="text-slate-500">Consulta</dt><dd>{data.appointment_number}</dd></div>
            <div><dt className="text-slate-500">Médico</dt><dd>{data.medico?.full_name ?? "—"}</dd></div>
            <div><dt className="text-slate-500">Prioridade</dt><dd>{PRIORITY_LABELS[data.prioridade as keyof typeof PRIORITY_LABELS] ?? data.prioridade}</dd></div>
            <div><dt className="text-slate-500">Pedido</dt><dd>{formatDisplayDateTime(data.data_pedido)}</dd></div>
            {data.data_rececao && <div><dt className="text-slate-500">Receção</dt><dd>{formatDisplayDateTime(data.data_rececao)}</dd></div>}
            {data.data_colheita && <div><dt className="text-slate-500">Colheita</dt><dd>{formatDisplayDateTime(data.data_colheita)}</dd></div>}
            {data.data_conclusao && <div><dt className="text-slate-500">Conclusão</dt><dd>{formatDisplayDateTime(data.data_conclusao)}</dd></div>}
          </dl>
          <Link to={`/patients/${data.paciente.id}`} className="mt-4 inline-block text-sm text-primary-700 hover:underline">
            Ver ficha do paciente
          </Link>
        </Card>

        <Card title="Exames">
          <ul className="space-y-2 text-sm">
            {data.exames.map((e) => (
              <li key={e.id} className="flex justify-between border-b border-slate-100 pb-2">
                <span>{e.nome_exame}</span>
                <StatusBadge status={e.estado} />
              </li>
            ))}
          </ul>
          {!isFinal && (
            <div className="mt-4 flex flex-wrap gap-2">
              {data.estado === "PENDENTE" && (
                <Button onClick={() => actionMutation.mutate("receive")}>Receber</Button>
              )}
              {(data.estado === "RECEBIDO" || data.estado === "AGUARDANDO_COLHEITA") && (
                <>
                  <Button variant="secondary" onClick={() => actionMutation.mutate("collect")}>Colheita</Button>
                  <Button variant="secondary" onClick={() => actionMutation.mutate("start")}>Processar</Button>
                </>
              )}
              {data.estado === "EM_PROCESSAMENTO" && (
                <>
                  <Button onClick={() => actionMutation.mutate("finish")}>Concluir</Button>
                  <Link to={`/laboratory/results/new?pedido=${data.id}`}>
                    <Button variant="secondary">Registar resultado</Button>
                  </Link>
                </>
              )}
              {data.estado === "CONCLUIDO" && (
                <Link to={`/laboratory/results/new?pedido=${data.id}`}>
                  <Button variant="secondary">Registar resultado</Button>
                </Link>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
