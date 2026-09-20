import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

import { ErrorState, useToast } from "@/design-system";
import { LaboratoryFilters } from "@/features/laboratory/components/LaboratoryFilters";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { LaboratoryTable } from "@/features/laboratory/components/LaboratoryTable";
import { LaboratoryTableSkeleton } from "@/features/laboratory/components/LaboratorySkeleton";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { laboratoryService } from "@/services/laboratory";
import { getApiErrorMessage } from "@/utils/api-error";

export function LaboratoryPendingPage() {
  const { showToast } = useToast();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [estado, setEstado] = useState("");
  const [prioridade, setPrioridade] = useState("");
  const [dataPedido, setDataPedido] = useState("");
  /** Por defeito: prontos a trabalhar (já pagos na Receção). */
  const [estadoFaturacao, setEstadoFaturacao] = useState("REGULARIZADO");
  const debouncedSearch = useDebouncedValue(search, 300);

  const params = {
    q: debouncedSearch.trim() || undefined,
    estado: estado || undefined,
    prioridade: prioridade || undefined,
    data_pedido: dataPedido || undefined,
    estado_faturacao: estadoFaturacao || undefined,
  };

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-pending", params],
    queryFn: () => laboratoryService.getPending(params),
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["laboratory-pending"] });
    void queryClient.invalidateQueries({ queryKey: ["laboratory-today"] });
    void queryClient.invalidateQueries({ queryKey: ["laboratory-dashboard"] });
  };

  const receiveMutation = useMutation({
    mutationFn: (id: number) => laboratoryService.receive(id),
    onSuccess: () => {
      showToast("Pedido recebido.", "success");
      invalidate();
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const collectMutation = useMutation({
    mutationFn: (id: number) => laboratoryService.collect(id),
    onSuccess: () => {
      showToast("Colheita registada.", "success");
      invalidate();
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const startMutation = useMutation({
    mutationFn: (id: number) => laboratoryService.start(id),
    onSuccess: (_data, id) => {
      showToast("Processamento iniciado.", "success");
      invalidate();
      void navigate(`/laboratory/results/new?pedido=${id}`);
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const finishMutation = useMutation({
    mutationFn: (id: number) => laboratoryService.finish(id),
    onSuccess: () => {
      showToast("Processamento concluído.", "success");
      invalidate();
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Fila de trabalho</h1>
        <p className="mt-1 text-slate-500">
          Por defeito só exames já regularizados na Receção. Altere o filtro para ver os que ainda
          aguardam pagamento.
        </p>
      </div>
      <LaboratorySubNav />
      <LaboratoryFilters
        search={search}
        onSearchChange={setSearch}
        estado={estado}
        onEstadoChange={setEstado}
        prioridade={prioridade}
        onPrioridadeChange={setPrioridade}
        dataPedido={dataPedido}
        onDataPedidoChange={setDataPedido}
        estadoFaturacao={estadoFaturacao}
        onEstadoFaturacaoChange={setEstadoFaturacao}
      />
      {isLoading ? (
        <LaboratoryTableSkeleton />
      ) : isError ? (
        <ErrorState message="Erro ao carregar pedidos." onRetry={() => void refetch()} />
      ) : (
        <LaboratoryTable
          orders={data?.results ?? []}
          onReceive={(o) => receiveMutation.mutate(o.id)}
          onCollect={(o) => collectMutation.mutate(o.id)}
          onStart={(o) => startMutation.mutate(o.id)}
          onFinish={(o) => finishMutation.mutate(o.id)}
          emptyTitle="Sem pedidos neste filtro"
          emptyDescription="Experimente «Todos» em regularização ou limpe os filtros."
        />
      )}
    </div>
  );
}
