import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Button, Card, LoadingState, Table } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { billingService } from "@/services/billing/billing.service";
import type { Quote } from "@/types/billing";

export function QuotesListPage() {
  const { data, isLoading } = useQuery({ queryKey: ["billing-quotes"], queryFn: () => billingService.listQuotes() });

  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <h2 className="text-2xl font-bold">Orçamentos</h2>
        <Link to="/billing/quotes/new"><Button variant="primary">Novo orçamento</Button></Link>
      </div>
      <BillingSubNav />
      {isLoading || !data ? <LoadingState /> : (
        <Card>
          <Table<Quote>
            data={data.results}
            getRowKey={(r) => r.id}
            columns={[
              { key: "numero", header: "Número" },
              { key: "paciente_nome", header: "Paciente" },
              { key: "estado", header: "Estado" },
              { key: "total", header: "Total", render: (r) => `${r.total} FCFA` },
            ]}
          />
        </Card>
      )}
    </div>
  );
}
