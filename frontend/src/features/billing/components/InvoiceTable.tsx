import { Link } from "react-router-dom";

import { Table } from "@/design-system";
import { InvoiceStatusBadge } from "@/features/billing/components/InvoiceStatusBadge";
import { formatCurrency } from "@/features/billing/utils/formatBilling";
import type { Invoice } from "@/types/billing";
import { formatDisplayDateTime } from "@/utils/date";

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
          render: (row) => <InvoiceStatusBadge estado={row.estado} />,
        },
        {
          key: "total",
          header: "Total",
          render: (row) => <span className="font-medium text-slate-900">{formatCurrency(row.total)}</span>,
        },
        {
          key: "emitida_em",
          header: "Emitida",
          render: (row) => (row.emitida_em ? formatDisplayDateTime(row.emitida_em) : "—"),
        },
      ]}
    />
  );
}
