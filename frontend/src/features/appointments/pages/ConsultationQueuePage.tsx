import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { Card, ErrorState, LoadingState, Pagination, useToast } from "@/design-system";
import { CONSULTATION_PAGE_SIZE } from "@/constants/appointments";
import { ConsultationQueueTable } from "@/features/appointments/components/ConsultationQueueTable";
import { ConsultationSubNav } from "@/features/appointments/components/ConsultationSubNav";
import { appointmentsService } from "@/services/appointments";
import type { Appointment } from "@/types/appointment";
import { getApiErrorMessage } from "@/utils/api-error";

export function ConsultationQueuePage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["consultation-queue", page],
    queryFn: () => appointmentsService.getQueue({ page }),
    refetchInterval: 30_000,
  });

  const startMutation = useMutation({
    mutationFn: (appointment: Appointment) => appointmentsService.start(appointment.id),
    onSuccess: (updated) => {
      showToast("Consulta iniciada.", "success");
      void queryClient.invalidateQueries({ queryKey: ["consultation-queue"] });
      navigate(`/consultations/${updated.id}`);
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const appointments = data?.results ?? [];
  const totalPages = Math.max(1, Math.ceil((data?.count ?? 0) / CONSULTATION_PAGE_SIZE));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Fila médica</h2>
        <p className="mt-1 text-slate-600">Utentes encaminhados pela receção, prontos para consulta.</p>
      </div>

      <ConsultationSubNav />

      <Card>
        {isLoading ? (
          <LoadingState message="A carregar fila médica..." />
        ) : isError ? (
          <ErrorState message="Não foi possível carregar a fila." onRetry={() => void refetch()} />
        ) : (
          <>
            <ConsultationQueueTable
              appointments={appointments}
              onStart={(appointment) => startMutation.mutate(appointment)}
              onOpen={(appointment) => navigate(`/consultations/${appointment.id}`)}
            />
            <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
              <span className="text-sm text-slate-600">Total: {data?.count ?? 0}</span>
              <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
