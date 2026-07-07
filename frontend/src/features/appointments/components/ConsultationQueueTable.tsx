import { Link } from "react-router-dom";

import { Button, Table } from "@/design-system";
import {
  AppointmentPatientCell,
  AppointmentStatusBadge,
} from "@/features/appointments/components/AppointmentStatusBadge";
import type { Appointment } from "@/types/appointment";
import { formatDisplayDateTime } from "@/utils/date";

interface ConsultationQueueTableProps {
  appointments: Appointment[];
  onStart?: (appointment: Appointment) => void;
  onOpen?: (appointment: Appointment) => void;
  showStartAction?: boolean;
}

export function ConsultationQueueTable({
  appointments,
  onStart,
  onOpen,
  showStartAction = true,
}: ConsultationQueueTableProps) {
  return (
    <Table<Appointment>
      data={appointments}
      getRowKey={(row) => row.id}
      emptyMessage="Nenhum utente na fila médica."
      columns={[
        {
          key: "patient",
          header: "Paciente",
          render: (row) => <AppointmentPatientCell appointment={row} />,
        },
        {
          key: "status",
          header: "Estado",
          render: (row) => <AppointmentStatusBadge status={row.status} />,
        },
        {
          key: "scheduled_at",
          header: "Agendado",
          render: (row) => formatDisplayDateTime(row.scheduled_at),
        },
        {
          key: "chief_complaint",
          header: "Queixa",
          render: (row) => row.chief_complaint || row.notes || "—",
        },
        {
          key: "actions",
          header: "Acções",
          render: (row) => (
            <div className="flex flex-wrap gap-2">
              {showStartAction && (row.status === "CONFIRMADA" || row.status === "EM_ESPERA") && onStart && (
                <Button size="sm" variant="primary" onClick={() => onStart(row)}>
                  Iniciar
                </Button>
              )}
                {row.status === "EM_CONSULTA" && onOpen && (
                <Button size="sm" variant="secondary" onClick={() => onOpen(row)}>
                  Consulta
                </Button>
              )}
              <Link to={`/patients/${row.patient.id}`}>
                <Button size="sm" variant="outline">
                  Ficha
                </Button>
              </Link>
            </div>
          ),
        },
      ]}
    />
  );
}
