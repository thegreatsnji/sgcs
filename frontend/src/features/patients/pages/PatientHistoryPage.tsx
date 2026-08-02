import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";

import {
  Badge,
  Card,
  EmptyState,
  ErrorState,
  LoadingState,
  Pagination,
  Table,
} from "@/design-system";
import { PatientProfileShell } from "@/features/patients/components/PatientProfileShell";
import { SelectField } from "@/features/patients/components/SelectField";
import { HISTORY_EVENT_TYPE_LABELS, PATIENT_PAGE_SIZE } from "@/constants/patients";
import { patientsService } from "@/services/patients";
import type { AuditTrailEntry, HistoryEventType } from "@/types/patient";
import { formatDisplayDate } from "@/utils/date";

type HistoryView = "timeline" | "audit";

export function PatientHistoryPage() {
  const { id } = useParams();
  const patientId = Number(id);
  const [view, setView] = useState<HistoryView>("timeline");
  const [page, setPage] = useState(1);
  const [eventType, setEventType] = useState<HistoryEventType | "">("");

  const { data: patient, isLoading: patientLoading } = useQuery({
    queryKey: ["patient", id],
    queryFn: () => patientsService.get(patientId),
  });

  const {
    data: timeline,
    isLoading: timelineLoading,
    isError: timelineError,
    refetch: refetchTimeline,
  } = useQuery({
    queryKey: ["patient-history", id, page, eventType],
    queryFn: () =>
      patientsService.listHistory(patientId, {
        page,
        event_type: eventType || undefined,
      }),
    enabled: Boolean(id) && view === "timeline",
  });

  const {
    data: audit,
    isLoading: auditLoading,
    isError: auditError,
    refetch: refetchAudit,
  } = useQuery({
    queryKey: ["patient-audit", id, page],
    queryFn: () => patientsService.listAuditTrail(patientId, { page }),
    enabled: Boolean(id) && view === "audit",
  });

  const isLoading = patientLoading || (view === "timeline" ? timelineLoading : auditLoading);
  const isError = view === "timeline" ? timelineError : auditError;
  const refetch = view === "timeline" ? refetchTimeline : refetchAudit;
  const history = view === "timeline" ? timeline : audit;

  if (isLoading) return <LoadingState message="A carregar histórico..." />;
  if (isError || !patient) {
    return <ErrorState message="Não foi possível carregar o histórico." onRetry={() => void refetch()} />;
  }

  const totalPages = Math.max(1, Math.ceil((history?.count ?? 0) / PATIENT_PAGE_SIZE));

  return (
    <PatientProfileShell patient={patient}>
      <Card>
        <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
          <div className="flex gap-2">
            <button
              type="button"
              className={`rounded-lg px-4 py-2 text-sm font-medium ${
                view === "timeline" ? "bg-primary-600 text-white" : "bg-slate-100 text-slate-700"
              }`}
              onClick={() => {
                setView("timeline");
                setPage(1);
              }}
            >
              Linha temporal
            </button>
            <button
              type="button"
              className={`rounded-lg px-4 py-2 text-sm font-medium ${
                view === "audit" ? "bg-primary-600 text-white" : "bg-slate-100 text-slate-700"
              }`}
              onClick={() => {
                setView("audit");
                setPage(1);
              }}
            >
              Auditoria
            </button>
          </div>

          {view === "timeline" && (
            <div className="w-full max-w-xs">
              <SelectField
                label="Tipo de evento"
                placeholder="Todos"
                value={eventType}
                onChange={(event) => {
                  setEventType(event.target.value as HistoryEventType | "");
                  setPage(1);
                }}
                options={(Object.entries(HISTORY_EVENT_TYPE_LABELS) as [HistoryEventType, string][]).map(
                  ([value, label]) => ({ value, label }),
                )}
              />
            </div>
          )}
        </div>

        {view === "timeline" ? (
          timeline?.results.length ? (
            <div className="space-y-4">
              {timeline.results.map((entry) => (
                <div key={entry.id} className="rounded-lg border border-slate-200 p-4">
                  <div className="mb-2 flex flex-wrap items-center gap-2">
                    <Badge variant="info">{HISTORY_EVENT_TYPE_LABELS[entry.event_type]}</Badge>
                    <span className="text-xs text-slate-500">{entry.event_date}</span>
                  </div>
                  <h3 className="font-medium text-slate-900">{entry.title}</h3>
                  {entry.description && <p className="mt-1 text-sm text-slate-600">{entry.description}</p>}
                  {entry.recorded_by && (
                    <p className="mt-2 text-xs text-slate-500">Por {entry.recorded_by.full_name}</p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <EmptyState title="Sem eventos" description="Ainda não existem eventos na linha temporal." />
          )
        ) : audit?.results.length ? (
          <Table<AuditTrailEntry>
            getRowKey={(row) => row.id}
            data={audit.results}
            columns={[
              { key: "action", header: "Ação" },
              { key: "description", header: "Descrição" },
              {
                key: "user",
                header: "Utilizador",
                render: (row) => row.user?.full_name ?? "—",
              },
              {
                key: "created_at",
                header: "Data",
                render: (row) => formatDisplayDate(row.created_at),
              },
            ]}
          />
        ) : (
          <EmptyState title="Sem auditoria" description="Não existem registos de auditoria." />
        )}

        <div className="mt-4 flex justify-end">
          <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
        </div>
      </Card>
    </PatientProfileShell>
  );
}
