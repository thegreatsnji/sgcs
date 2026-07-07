import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import {
  Card,
  ErrorState,
  LoadingState,
  Modal,
  Pagination,
  useToast,
} from "@/design-system";
import { RECEPTION_PAGE_SIZE } from "@/constants/reception";
import { QueueTable } from "@/features/reception/components/QueueTable";
import { ReceptionSubNav } from "@/features/reception/components/ReceptionSubNav";
import { useReceptionQueue } from "@/features/reception/hooks/useReceptionQueue";
import { receptionService } from "@/services/reception";
import type { WaitingQueueEntry } from "@/types/reception";
import { getApiErrorMessage } from "@/utils/api-error";

export function WaitingQueuePage() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [assignTarget, setAssignTarget] = useState<WaitingQueueEntry | null>(null);

  const { data, isLoading, isError, refetch } = useReceptionQueue(page);

  const assignMutation = useMutation({
    mutationFn: (entry: WaitingQueueEntry) =>
      receptionService.assignToDoctor({ queue_id: entry.id }),
    onSuccess: () => {
      showToast("Paciente encaminhado para médico.", "success");
      setAssignTarget(null);
      void queryClient.invalidateQueries({ queryKey: ["reception-queue"] });
      void queryClient.invalidateQueries({ queryKey: ["reception-dashboard"] });
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const callMutation = useMutation({
    mutationFn: (entry: WaitingQueueEntry) =>
      receptionService.updateQueueEntry(entry.id, { status: "CALLED" }),
    onSuccess: () => {
      showToast("Utente chamado.", "success");
      void queryClient.invalidateQueries({ queryKey: ["reception-queue"] });
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const entries = data?.results ?? [];
  const totalPages = Math.max(1, Math.ceil((data?.count ?? 0) / RECEPTION_PAGE_SIZE));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Fila de espera</h2>
        <p className="mt-1 text-slate-600">Gestão da fila de utentes em espera de atendimento.</p>
      </div>

      <ReceptionSubNav />

      <Card>
        {isLoading ? (
          <LoadingState message="A carregar fila..." />
        ) : isError ? (
          <ErrorState message="Não foi possível carregar a fila." onRetry={() => void refetch()} />
        ) : (
          <>
            <QueueTable
              entries={entries}
              onAssign={(entry) => setAssignTarget(entry)}
              onUpdateStatus={(entry) => callMutation.mutate(entry)}
            />
            <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
              <span className="text-sm text-slate-600">Total: {data?.count ?? 0}</span>
              <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
            </div>
          </>
        )}
      </Card>

      <Modal
        open={Boolean(assignTarget)}
        title="Encaminhar para médico"
        description={`Confirma o encaminhamento de ${assignTarget?.patient.full_name} para consulta médica?`}
        confirmLabel="Encaminhar"
        onConfirm={() => assignTarget && assignMutation.mutate(assignTarget)}
        onClose={() => setAssignTarget(null)}
      />
    </div>
  );
}
