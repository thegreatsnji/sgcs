import { Link } from "react-router-dom";

import { Badge, Table } from "@/design-system";
import type { Invoice } from "@/types/billing";
import { formatDisplayDateTime } from "@/utils/date";

const ESTADO_VARIANT: Record<string, "default" | "success" | "warning" | "danger" | "info"> = {
  PENDENTE: "warning",
  PARCIAL: "info",
  PAGA: "success",
  CANCELADA: "default",
};

const ESTADO_LABEL: Record<string, string> = {
  PENDENTE: "Pendente",
  PARCIAL: "Parcial",
  PAGA: "Paga",
  CANCELADA: "Cancelada",
};

interface InvoiceTableProps {
  invoices: Invoice[];
  emptyMessage?: string;
}

export function InvoiceTable({ invoices, emptyMessage = "Sem faturas." }: InvoiceTableProps) {
  return (
    <Table<Invoice>
      data={invoices}
      getRowKey={(row) => row.id}
      emptyMessage={emptyMessage}
      columns={[
        {
          key: "numero",
          header: "Número",
          render: (row) => (
            <Link to={`/billing/invoices/${row.id}`} className="font-medium text-primary-700 hover:underline">
              {row.numero}
            </Link>
          ),
        },
        { key: "paciente_nome", header: "Paciente" },
        {
          key: "estado",
          header: "Estado",
          render: (row) => <Badge variant={ESTADO_VARIANT[row.estado]}>{ESTADO_LABEL[row.estado]}</Badge>,
        },
        { key: "total", header: "Total", render: (row) => `${row.total} FCFA` },
        {
          key: "emitida_em",
          header: "Emitida",
          render: (row) => (row.emitida_em ? formatDisplayDateTime(row.emitida_em) : "—"),
        },
      ]}
    />
  );
}
