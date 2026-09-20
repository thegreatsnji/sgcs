import { useQuery } from "@tanstack/react-query";
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
import { ReceptionDoctorNotifyPanel } from "@/features/reception/components/ReceptionDoctorNotifyPanel";
import { ReceptionSubNav } from "@/features/reception/components/ReceptionSubNav";
import { useReceptionQueue } from "@/features/reception/hooks/useReceptionQueue";
import { receptionService } from "@/services/reception";
import type { WaitingQueueEntry } from "@/types/reception";
import { getApiErrorMessage } from "@/utils/api-error";

type DoctorFilter = "all" | "unassigned" | number;

export function WaitingQueuePage() {
  const { showToast } = useToast();
  const [page, setPage] = useState(1);
  const [doctorFilter, setDoctorFilter] = useState<DoctorFilter>("all");
  const [assignTarget, setAssignTarget] = useState<WaitingQueueEntry | null>(null);

  const queueParams =
    doctorFilter === "all"
      ? { page }
      : doctorFilter === "unassigned"
        ? { page, unassigned: true as const }
        : { page, doctor: doctorFilter };

  const { data, isLoading, isError, refetch } = useReceptionQueue(queueParams);

  const { data: doctorOptions } = useQuery({
    queryKey: ["reception-queue-doctor-filter"],
    queryFn: async () => {
      const opts = await receptionService.getDoctorAssignmentOptions();
      return { doctors: opts.doctors.map((d) => ({ id: d.id, full_name: d.full_name })) };
    },
  });

  const callMutationStatus = async (entry: WaitingQueueEntry) => {
    try {
      await receptionService.updateQueueEntry(entry.id, { status: "CALLED" });
      showToast("Utente chamado.", "success");
      void refetch();
    } catch (error) {
      showToast(getApiErrorMessage(error), "error");
    }
  };

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
        <div className="mb-4 flex flex-wrap items-end gap-3">
          <div className="min-w-[14rem]">
            <label htmlFor="queue-doctor-filter" className="mb-1 block text-sm font-medium text-slate-700">
              Filtrar por médico
            </label>
            <select
              id="queue-doctor-filter"
              className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
              value={doctorFilter === "all" || doctorFilter === "unassigned" ? doctorFilter : String(doctorFilter)}
              onChange={(e) => {
                const v = e.target.value;
                setPage(1);
                if (v === "all" || v === "unassigned") setDoctorFilter(v);
                else setDoctorFilter(Number(v));
              }}
            >
              <option value="all">Todos os médicos</option>
              <option value="unassigned">Por atribuir</option>
              {(doctorOptions?.doctors ?? []).map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.full_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {isLoading ? (
          <LoadingState message="A carregar fila..." />
        ) : isError ? (
          <ErrorState message="Não foi possível carregar a fila." onRetry={() => void refetch()} />
        ) : (
          <>
            <QueueTable
              entries={entries}
              onAssign={(entry) => setAssignTarget(entry)}
              onUpdateStatus={(entry) => void callMutationStatus(entry)}
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
        title={assignTarget?.assigned_doctor ? "Alterar médico" : "Encaminhar para médico"}
        description={
          assignTarget
            ? `${assignTarget.patient.full_name} · ${assignTarget.patient.patient_number}`
            : undefined
        }
        cancelLabel="Fechar"
        onClose={() => setAssignTarget(null)}
      >
        {assignTarget ? (
          <ReceptionDoctorNotifyPanel
            queueEntryId={assignTarget.id}
            patientId={assignTarget.patient.id}
            patientName={assignTarget.patient.full_name}
            checkInId={assignTarget.check_in_id}
            paymentConfirmed
            reassign={Boolean(assignTarget.assigned_doctor)}
            onNotified={() => {
              setAssignTarget(null);
              void refetch();
            }}
            onSkip={() => setAssignTarget(null)}
          />
        ) : null}
      </Modal>
    </div>
  );
}
