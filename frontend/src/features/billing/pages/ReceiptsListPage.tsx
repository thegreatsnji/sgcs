import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Card, LoadingState, Table } from "@/design-system";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { billingService } from "@/services/billing/billing.service";
import type { Receipt } from "@/types/billing";
import { formatDisplayDateTime } from "@/utils/date";

export function ReceiptsListPage() {
  const { data, isLoading } = useQuery({ queryKey: ["billing-receipts"], queryFn: () => billingService.listReceipts() });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Recibos</h2>
      <BillingSubNav />
      {isLoading || !data ? <LoadingState /> : (
        <Card>
          <Table<Receipt>
            data={data.results}
            getRowKey={(r) => r.id}
            columns={[
              { key: "numero", header: "Número", render: (r) => <Link to={`/billing/receipts/${r.id}`} className="text-primary-700">{r.numero}</Link> },
              { key: "paciente_nome", header: "Paciente" },
              { key: "fatura_numero", header: "Fatura" },
              { key: "pagamento_valor", header: "Valor", render: (r) => `${r.pagamento_valor} FCFA` },
              { key: "emitido_em", header: "Emitido", render: (r) => formatDisplayDateTime(r.emitido_em) },
            ]}
          />
        </Card>
      )}
    </div>
  );
}
