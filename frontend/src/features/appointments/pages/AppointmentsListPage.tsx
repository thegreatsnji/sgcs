import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { Card, LoadingState, Pagination, useToast } from "@/design-system";
import { APPOINTMENT_PAGE_SIZE } from "@/constants/appointments";
import { AppointmentSubNav } from "@/features/appointments/components/AppointmentSubNav";
import { AppointmentTable } from "@/features/appointments/components/AppointmentTable";
import { appointmentsService } from "@/services/appointments";
import { getApiErrorMessage } from "@/utils/api-error";

export function AppointmentsListPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["appointments-list", page, status],
    queryFn: () => appointmentsService.list({ page, status: status || undefined }),
  });

  const confirmMutation = useMutation({
    mutationFn: (id: number) => appointmentsService.confirm(id),
    onSuccess: () => {
      showToast("Consulta confirmada.", "success");
      void queryClient.invalidateQueries({ queryKey: ["appointments-list"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const startMutation = useMutation({
    mutationFn: (id: number) => appointmentsService.start(id),
    onSuccess: (updated) => {
      showToast("Consulta iniciada.", "success");
      navigate(`/appointments/${updated.id}`);
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const totalPages = Math.max(1, Math.ceil((data?.count ?? 0) / APPOINTMENT_PAGE_SIZE));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Lista de Consultas</h2>
      </div>
      <AppointmentSubNav />
      <Card>
        <div className="mb-4">
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            <option value="">Todos os estados</option>
            <option value="AGENDADA">Agendada</option>
            <option value="CONFIRMADA">Confirmada</option>
            <option value="EM_ESPERA">Em espera</option>
            <option value="EM_CONSULTA">Em consulta</option>
            <option value="CONCLUIDA">Concluída</option>
          </select>
        </div>
        {isLoading ? (
          <LoadingState message="A carregar consultas..." />
        ) : (
          <>
            <AppointmentTable
              appointments={data?.results ?? []}
              onConfirm={(a) => confirmMutation.mutate(a.id)}
              onStart={(a) => startMutation.mutate(a.id)}
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
