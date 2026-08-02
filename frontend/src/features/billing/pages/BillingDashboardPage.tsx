import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Card, ErrorState } from "@/design-system";
import { BillingCharts } from "@/features/billing/components/BillingCharts";
import { BillingDashboardCards } from "@/features/billing/components/BillingDashboardCards";
import { BillingDashboardSkeleton } from "@/features/billing/components/BillingSkeleton";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { InvoiceTable } from "@/features/billing/components/InvoiceTable";
import { billingService } from "@/services/billing/billing.service";
import { reportsService } from "@/services/reports/reports.service";

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

  const { data: charts } = useQuery({
    queryKey: ["reports-charts"],
    queryFn: reportsService.getCharts,
  });

  const { data: payments } = useQuery({
    queryKey: ["billing-payments-preview"],
    queryFn: () => billingService.listPayments({ page: 1, page_size: 100 }),
  });

  if (isLoading || !data) return <BillingDashboardSkeleton />;
  if (isError) return <ErrorState message="Não foi possível carregar o painel." onRetry={() => void refetch()} />;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Faturação</h1>
          <p className="mt-1 text-slate-500">Painel executivo de receitas, faturas e pagamentos.</p>
        </div>
        <Link
          to="/billing/invoices"
          className="inline-flex items-center justify-center rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-medium text-white shadow-md shadow-primary-600/20 transition hover:bg-primary-700"
        >
          Ver todas as faturas
        </Link>
      </div>

      <BillingSubNav />
      <BillingDashboardCards data={data} />

      <BillingCharts
        revenueTrend={charts?.receitas ?? []}
        services={data.servicos_mais_vendidos}
        payments={payments?.results ?? []}
      />

      {invoices && (
        <Card title="Faturas recentes">
          <InvoiceTable invoices={invoices.results} />
        </Card>
      )}
    </div>
  );
}
