import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { Avatar, Button, Card, ErrorState, LoadingState, useToast } from "@/design-system";
import { PRIORITY_LABELS } from "@/constants/appointments";
import { LabWorkflowProgress } from "@/features/laboratory/components/LabWorkflowProgress";
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
    <div className="space-y-6 pb-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-4">
          <Avatar name={data.paciente.full_name} size="lg" />
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{data.numero_pedido}</h1>
            <p className="text-slate-600">{data.paciente.full_name}</p>
            <p className="text-sm text-slate-500">{data.paciente.patient_number}</p>
          </div>
        </div>
        <StatusBadge status={data.estado} />
      </div>

      <LaboratorySubNav />

      <Card>
        <h2 className="mb-4 text-sm font-semibold text-slate-900">Progresso do fluxo laboratorial</h2>
        <LabWorkflowProgress status={data.estado} />
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Informação do pedido">
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between gap-4 border-b border-slate-50 pb-2">
              <dt className="text-slate-500">Consulta</dt>
              <dd className="font-medium">{data.appointment_number}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-slate-50 pb-2">
              <dt className="text-slate-500">Médico</dt>
              <dd className="font-medium">{data.medico?.full_name ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-slate-50 pb-2">
              <dt className="text-slate-500">Prioridade</dt>
              <dd className="font-medium">
                {PRIORITY_LABELS[data.prioridade as keyof typeof PRIORITY_LABELS] ?? data.prioridade}
              </dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-slate-50 pb-2">
              <dt className="text-slate-500">Pedido</dt>
              <dd>{formatDisplayDateTime(data.data_pedido)}</dd>
            </div>
            {data.data_rececao && (
              <div className="flex justify-between gap-4 border-b border-slate-50 pb-2">
                <dt className="text-slate-500">Receção</dt>
                <dd>{formatDisplayDateTime(data.data_rececao)}</dd>
              </div>
            )}
            {data.data_colheita && (
              <div className="flex justify-between gap-4 border-b border-slate-50 pb-2">
                <dt className="text-slate-500">Colheita</dt>
                <dd>{formatDisplayDateTime(data.data_colheita)}</dd>
              </div>
            )}
            {data.data_conclusao && (
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Conclusão</dt>
                <dd>{formatDisplayDateTime(data.data_conclusao)}</dd>
              </div>
            )}
          </dl>
          <Link to={`/patients/${data.paciente.id}`} className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-700">
            Ver ficha do paciente →
          </Link>
        </Card>

        <Card title="Exames solicitados">
          <ul className="divide-y divide-slate-100">
            {data.exames.map((e) => (
              <li key={e.id} className="flex items-center justify-between py-3 first:pt-0">
                <div>
                  <p className="font-medium text-slate-900">{e.nome_exame}</p>
                  <p className="text-xs text-slate-500">{e.categoria}</p>
                </div>
                <StatusBadge status={e.estado} />
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {!isFinal && (
        <div className="sticky bottom-0 z-10 -mx-4 border-t border-slate-200 bg-white/95 px-4 py-4 backdrop-blur-md lg:-mx-0 lg:rounded-2xl lg:border lg:shadow-sm">
          <div className="flex flex-wrap gap-2">
            {data.estado === "PENDENTE" && (
              <Button onClick={() => actionMutation.mutate("receive")}>Receber pedido</Button>
            )}
            {(data.estado === "RECEBIDO" || data.estado === "AGUARDANDO_COLHEITA") && (
              <>
                <Button variant="secondary" onClick={() => actionMutation.mutate("collect")}>Registar colheita</Button>
                <Button variant="secondary" onClick={() => actionMutation.mutate("start")}>Iniciar processamento</Button>
              </>
            )}
            {data.estado === "EM_PROCESSAMENTO" && (
              <>
                <Button onClick={() => actionMutation.mutate("finish")}>Concluir pedido</Button>
                <Link to={`/laboratory/results/new?pedido=${data.id}`}>
                  <Button variant="secondary">Registar resultado</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      )}

      {data.estado === "CONCLUIDO" && (
        <div className="flex gap-2">
          <Link to={`/laboratory/results/new?pedido=${data.id}`}>
            <Button variant="primary">Registar resultado</Button>
          </Link>
        </div>
      )}
    </div>
  );
}
