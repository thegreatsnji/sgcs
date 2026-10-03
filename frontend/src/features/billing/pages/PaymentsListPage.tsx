import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Card, LoadingState, Table } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { billingService } from "@/services/billing/billing.service";
import type { Payment } from "@/types/billing";
import { formatDisplayDateTime } from "@/utils/date";

export function PaymentsListPage() {
  const { data, isLoading } = useQuery({ queryKey: ["billing-payments"], queryFn: () => billingService.listPayments() });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Pagamentos</h2>
      <BillingSubNav />
      {isLoading || !data ? <LoadingState /> : (
        <Card>
          <Table<Payment>
            data={data.results}
            getRowKey={(r) => r.id}
            columns={[
              { key: "fatura_numero", header: "Fatura", render: (r) => <Link to={`/billing/invoices/${r.fatura}`} className="text-primary-700">{r.fatura_numero}</Link> },
              { key: "valor", header: "Valor", render: (r) => `${r.valor} FCFA` },
              { key: "metodo_pagamento", header: "Método" },
              { key: "estado", header: "Estado" },
              { key: "data_pagamento", header: "Data", render: (r) => r.data_pagamento ? formatDisplayDateTime(r.data_pagamento) : "—" },
            ]}
          />
        </Card>
      )}
    </div>
  );
}
