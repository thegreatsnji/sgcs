import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { InvoiceTable } from "@/features/billing/components/InvoiceTable";
import { billingService } from "@/services/billing/billing.service";

export function InvoicesListPage() {
  const { data } = useQuery({ queryKey: ["billing-invoices"], queryFn: () => billingService.listInvoices() });

  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <h2 className="text-2xl font-bold">Faturas</h2>
        <Link to="/billing/invoices/new"><Button variant="primary">Nova fatura</Button></Link>
      </div>
      <BillingSubNav />
      {data && <InvoiceTable invoices={data.results} />}
    </div>
  );
}
