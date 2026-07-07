import { useQuery } from "@tanstack/react-query";

import { Card, ErrorState, LoadingState } from "@/design-system";
import { BillingDashboardCards } from "@/features/billing/components/BillingDashboardCards";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { InvoiceTable } from "@/features/billing/components/InvoiceTable";
import { billingService } from "@/services/billing/billing.service";

export function BillingDashboardPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["billing-dashboard"],
    queryFn: billingService.getDashboard,
    refetchInterval: 30_000,
  });

  const { data: invoices } = useQuery({
    queryKey: ["billing-invoices-preview"],
    queryFn: () => billingService.listInvoices({ page: 1 }),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Faturação</h2>
        <p className="mt-1 text-slate-600">Painel financeiro e indicadores.</p>
      </div>
      <BillingSubNav />

      {isLoading || !data ? (
        <LoadingState message="A carregar indicadores..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar o painel." onRetry={() => void refetch()} />
      ) : (
        <>
          <BillingDashboardCards data={data} />
          {data.servicos_mais_vendidos.length > 0 && (
            <Card title="Serviços mais vendidos">
              <ul className="space-y-1 text-sm">
                {data.servicos_mais_vendidos.map((s) => (
                  <li key={s.servico} className="flex justify-between">
                    <span>{s.servico}</span>
                    <span className="font-medium">{s.quantidade}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </>
      )}

      {invoices && (
        <Card title="Faturas recentes">
          <InvoiceTable invoices={invoices.results} />
        </Card>
      )}
    </div>
  );
}
