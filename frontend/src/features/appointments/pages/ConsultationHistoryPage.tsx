import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { Card, ErrorState, LoadingState, Pagination, Table } from "@/design-system";
import { AppointmentStatusBadge } from "@/features/appointments/components/AppointmentStatusBadge";
import { ConsultationSubNav } from "@/features/appointments/components/ConsultationSubNav";
import { CONSULTATION_PAGE_SIZE } from "@/constants/appointments";
import { appointmentsService } from "@/services/appointments";
import type { Appointment } from "@/types/appointment";
import { formatDisplayDateTime } from "@/utils/date";

export function ConsultationHistoryPage() {
  const [page, setPage] = useState(1);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["appointments-history", page],
    queryFn: () => appointmentsService.list({ page, status: "CONCLUIDA" }),
  });

  const appointments = data?.results ?? [];
  const totalPages = Math.max(1, Math.ceil((data?.count ?? 0) / CONSULTATION_PAGE_SIZE));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Histórico de consultas</h2>
        <p className="mt-1 text-slate-600">Consultas concluídas.</p>
      </div>

      <ConsultationSubNav />

      <Card>
        {isLoading ? (
          <LoadingState message="A carregar histórico..." />
        ) : isError ? (
          <ErrorState message="Não foi possível carregar o histórico." onRetry={() => void refetch()} />
        ) : (
          <>
            <Table<Appointment>
              data={appointments}
              getRowKey={(row) => row.id}
              emptyMessage="Sem consultas concluídas."
              columns={[
                {
                  key: "patient",
                  header: "Paciente",
                  render: (row) => (
                    <Link to={`/patients/${row.patient.id}`} className="font-medium text-primary-700 hover:underline">
                      {row.patient.full_name}
                    </Link>
                  ),
                },
                {
                  key: "status",
                  header: "Estado",
                  render: (row) => <AppointmentStatusBadge status={row.status} />,
                },
                {
                  key: "scheduled_at",
                  header: "Data",
                  render: (row) => formatDisplayDateTime(row.completed_at ?? row.scheduled_at),
                },
                {
                  key: "diagnosis",
                  header: "Diagnóstico",
                  render: (row) => row.diagnosis || "—",
                },
                {
                  key: "doctor",
                  header: "Médico",
                  render: (row) => row.doctor?.full_name ?? "—",
                },
                {
                  key: "actions",
                  header: "Acções",
                  render: (row) => (
                    <Link to={`/consultations/${row.id}`}>
                      <span className="text-sm font-medium text-primary-700 hover:underline">Ver</span>
                    </Link>
                  ),
                },
              ]}
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
