import { Link } from "react-router-dom";

import { Button, Table } from "@/design-system";
import {
  AppointmentPatientCell,
  AppointmentStatusBadge,
} from "@/features/appointments/components/AppointmentStatusBadge";
import type { Appointment } from "@/types/appointment";
import { formatDisplayDateTime } from "@/utils/date";

interface AppointmentTableProps {
  appointments: Appointment[];
  onConfirm?: (a: Appointment) => void;
  onStart?: (a: Appointment) => void;
}

export function AppointmentTable({ appointments, onConfirm, onStart }: AppointmentTableProps) {
  return (
    <Table<Appointment>
      data={appointments}
      getRowKey={(row) => row.id}
      emptyMessage="Sem consultas registadas."
      columns={[
        { key: "patient", header: "Paciente", render: (row) => <AppointmentPatientCell appointment={row} /> },
        { key: "status", header: "Estado", render: (row) => <AppointmentStatusBadge status={row.status} /> },
        {
          key: "scheduled_at",
          header: "Data/Hora",
          render: (row) => formatDisplayDateTime(row.scheduled_at),
        },
        { key: "doctor", header: "Médico", render: (row) => row.doctor?.full_name ?? "—" },
        {
          key: "actions",
          header: "Acções",
          render: (row) => (
            <div className="flex flex-wrap gap-2">
              <Link to={`/appointments/${row.id}`}>
                <Button size="sm" variant="outline">
                  Ver
                </Button>
              </Link>
              {row.status === "AGENDADA" && onConfirm && (
                <Button size="sm" variant="secondary" onClick={() => onConfirm(row)}>
                  Confirmar
                </Button>
              )}
              {(row.status === "CONFIRMADA" || row.status === "EM_ESPERA") && onStart && (
                <Button size="sm" variant="primary" onClick={() => onStart(row)}>
                  Iniciar
                </Button>
              )}
            </div>
          ),
        },
      ]}
    />
  );
}
