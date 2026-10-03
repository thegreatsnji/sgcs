import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { Card, ErrorState, LoadingState, Pagination, useToast } from "@/design-system";
import { APPOINTMENT_PAGE_SIZE } from "@/constants/appointments";
import { AppointmentSubNav } from "@/features/appointments/components/AppointmentSubNav";
import { AppointmentTable } from "@/features/appointments/components/AppointmentTable";
import { appointmentsService } from "@/services/appointments";
import type { Appointment } from "@/types/appointment";
import { getApiErrorMessage } from "@/utils/api-error";

export function AppointmentsQueuePage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["appointments-queue", page],
    queryFn: () => appointmentsService.getQueue({ page }),
    refetchInterval: 30_000,
  });

  const startMutation = useMutation({
    mutationFn: (appointment: Appointment) => appointmentsService.start(appointment.id),
    onSuccess: (updated) => {
      showToast("Consulta iniciada.", "success");
      void queryClient.invalidateQueries({ queryKey: ["appointments-queue"] });
      navigate(`/appointments/${updated.id}`);
    },
    onError: (error) => showToast(getApiErrorMessage(error), "error"),
  });

  const totalPages = Math.max(1, Math.ceil((data?.count ?? 0) / APPOINTMENT_PAGE_SIZE));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Fila médica</h2>
        <p className="mt-1 text-slate-600">Utentes encaminhados pela receção.</p>
      </div>
      <AppointmentSubNav />
      <Card>
        {isLoading ? (
          <LoadingState message="A carregar fila..." />
        ) : isError ? (
          <ErrorState message="Erro ao carregar fila." onRetry={() => void refetch()} />
        ) : (
          <>
            <AppointmentTable
              appointments={data?.results ?? []}
              onStart={(a) => startMutation.mutate(a)}
            />
            <div className="mt-4 flex justify-between">
              <span className="text-sm text-slate-600">Total: {data?.count ?? 0}</span>
              <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
