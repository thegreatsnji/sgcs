import { Link } from "react-router-dom";

import { Card } from "@/design-system";
import { Badge } from "@/design-system";
import type { Invoice } from "@/types/billing";

interface InvoiceCardProps {
  invoice: Invoice;
}

export function InvoiceCard({ invoice }: InvoiceCardProps) {
  return (
    <Card title={invoice.numero}>
      <div className="space-y-2 text-sm">
        <p className="text-slate-600">{invoice.paciente_nome}</p>
        <Badge>{invoice.estado}</Badge>
        <p className="text-lg font-semibold text-primary-700">{invoice.total} FCFA</p>
        <Link to={`/billing/invoices/${invoice.id}`} className="text-primary-700 hover:underline">
          Ver detalhes
        </Link>
      </div>
    </Card>
  );
}
