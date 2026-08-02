import { Link } from "react-router-dom";

import { Button, Table } from "@/design-system";
import { PriorityBadge } from "@/features/reception/components/PriorityBadge";
import { QueueStatusBadge } from "@/features/reception/components/QueueStatusBadge";
import { TriageBadge } from "@/features/reception/components/TriageBadge";
import type { WaitingQueueEntry } from "@/types/reception";
import { formatDisplayDateTime } from "@/utils/date";

interface QueueTableProps {
  entries: WaitingQueueEntry[];
  onAssign?: (entry: WaitingQueueEntry) => void;
  onUpdateStatus?: (entry: WaitingQueueEntry) => void;
  showActions?: boolean;
}

export function QueueTable({ entries, onAssign, onUpdateStatus, showActions = true }: QueueTableProps) {
  return (
    <Table<WaitingQueueEntry>
      data={entries}
      getRowKey={(row) => row.id}
      emptyMessage="Nenhum utente na fila de espera."
      columns={[
        {
          key: "position",
          header: "#",
          render: (row) => <span className="font-semibold text-slate-900">{row.position}</span>,
        },
        {
          key: "patient",
          header: "Paciente",
          render: (row) => (
            <div>
              <Link
                to={`/patients/${row.patient.id}`}
                className="font-medium text-primary-700 hover:underline"
              >
                {row.patient.full_name}
              </Link>
              <p className="text-xs text-slate-500">{row.patient.patient_number}</p>
            </div>
          ),
        },
        {
          key: "triage",
          header: "Triagem",
          render: (row) => (
            <div className="space-y-1">
              <TriageBadge color={row.triage_color} />
              {!row.triage_color && <PriorityBadge priority={row.priority} />}
            </div>
          ),
        },
        {
          key: "priority",
          header: "Prioridade",
          render: (row) => <PriorityBadge priority={row.priority} />,
        },
        {
          key: "status",
          header: "Estado",
          render: (row) => <QueueStatusBadge status={row.status} />,
        },
        {
          key: "estimated_wait_minutes",
          header: "Tempo estimado",
          render: (row) =>
            row.estimated_wait_minutes != null ? `${row.estimated_wait_minutes} min` : "—",
        },
        {
          key: "check_in_time",
          header: "Entrada",
          render: (row) => formatDisplayDateTime(row.check_in_time),
        },
        ...(showActions
          ? [
              {
                key: "actions",
                header: "Acções",
                render: (row: WaitingQueueEntry) => (
                  <div className="flex flex-wrap gap-2">
                    {onAssign && row.status !== "IN_SERVICE" && row.status !== "COMPLETED" && (
                      <Button size="sm" variant="primary" onClick={() => onAssign(row)}>
                        Médico
                      </Button>
                    )}
                    {onUpdateStatus && row.status === "WAITING" && (
                      <Button size="sm" variant="secondary" onClick={() => onUpdateStatus(row)}>
                        Chamar
                      </Button>
                    )}
                  </div>
                ),
              },
            ]
          : []),
      ]}
    />
  );
}
