import { Link } from "react-router-dom";

import { Button, Table } from "@/design-system";
import { PriorityBadge } from "@/features/reception/components/PriorityBadge";
import { QueueStatusBadge } from "@/features/reception/components/QueueStatusBadge";
import { TriageBadge } from "@/features/reception/components/TriageBadge";
import {
  formatEstimatedWaitLabel,
  formatQueuePosition,
} from "@/features/reception/utils/formatQueueDisplay";
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
          header: "Posição",
          render: (row) => (
            <span className="font-medium text-slate-900">{formatQueuePosition(row.position)}</span>
          ),
        },
        {
          key: "patient",
          header: "Paciente",
          render: (row) => (
            <div className="min-w-0 max-w-[16rem]">
              <Link
                to={`/patients/${row.patient.id}`}
                className="break-words font-medium text-primary-700 hover:underline"
              >
                {row.patient.full_name}
              </Link>
              <p className="mt-0.5 text-xs text-slate-500">
                Utente: <span className="font-mono">{row.patient.patient_number}</span>
              </p>
            </div>
          ),
        },
        {
          key: "doctor",
          header: "Médico",
          render: (row) =>
            row.assigned_doctor?.full_name ? (
              <span className="text-sm text-slate-800">{row.assigned_doctor.full_name}</span>
            ) : (
              <span className="text-sm text-amber-700">Por atribuir</span>
            ),
        },
        {
          key: "triage",
          header: "Triagem",
          render: (row) => (
            <div className="flex flex-wrap gap-1">
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
          header: "Espera estimada",
          render: (row) => formatEstimatedWaitLabel(row.estimated_wait_minutes),
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
                render: (row: WaitingQueueEntry) => {
                  const canAssign =
                    onAssign &&
                    row.status !== "COMPLETED" &&
                    row.status !== "CANCELLED" &&
                    (row.can_reassign_doctor !== false || !row.assigned_doctor);
                  const label = row.assigned_doctor ? "Alterar médico" : "Atribuir médico";
                  return (
                    <div className="flex flex-wrap gap-2">
                      {canAssign ? (
                        <Button size="sm" variant="primary" onClick={() => onAssign(row)}>
                          {label}
                        </Button>
                      ) : null}
                      {onUpdateStatus && row.status === "WAITING" && (
                        <Button size="sm" variant="secondary" onClick={() => onUpdateStatus(row)}>
                          Chamar
                        </Button>
                      )}
                    </div>
                  );
                },
              },
            ]
          : []),
      ]}
    />
  );
}
