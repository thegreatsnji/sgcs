import { Link } from "react-router-dom";

import { Button, Table } from "@/design-system";
import { InvoiceStatusBadge } from "@/features/billing/components/InvoiceStatusBadge";
import { formatCurrency } from "@/features/billing/utils/formatBilling";
import type { Invoice } from "@/types/billing";
import { formatDisplayDateTime } from "@/utils/date";

interface InvoiceTableProps {
  invoices: Invoice[];
  emptyMessage?: string;
}

function invoiceSaldo(row: Invoice): number {
  if (row.saldo != null) return Math.max(0, Number(row.saldo));
  return Math.max(0, Number(row.total) - Number(row.total_pago));
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
          header: "Fatura",
          render: (row) => (
            <Link to={`/billing/invoices/${row.id}`} className="font-medium text-primary-700 hover:underline">
              {row.numero}
            </Link>
          ),
        },
        { key: "paciente_nome", header: "Utente" },
        {
          key: "estado",
          header: "Estado",
          render: (row) => <InvoiceStatusBadge estado={row.estado} />,
        },
        {
          key: "emitida_em",
          header: "Data",
          render: (row) => (row.emitida_em ? formatDisplayDateTime(row.emitida_em) : "—"),
        },
        {
          key: "total",
          header: "Total",
          render: (row) => <span className="font-medium text-slate-900">{formatCurrency(row.total)}</span>,
        },
        {
          key: "total_pago",
          header: "Pago",
          render: (row) => formatCurrency(row.total_pago),
        },
        {
          key: "saldo",
          header: "Saldo",
          render: (row) => {
            const saldo = invoiceSaldo(row);
            return (
              <span className={saldo > 0 ? "font-semibold text-amber-700" : "text-slate-600"}>
                {formatCurrency(saldo)}
              </span>
            );
          },
        },
        {
          key: "actions",
          header: "",
          render: (row) => (
            <Link to={`/billing/invoices/${row.id}`}>
              <Button size="sm" variant="outline">
                Ver fatura
              </Button>
            </Link>
          ),
        },
      ]}
    />
  );
}
