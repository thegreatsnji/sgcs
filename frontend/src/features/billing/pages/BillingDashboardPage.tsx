import { useQuery } from "@tanstack/react-query";

import { Card, ErrorState } from "@/design-system";
import { RoleDashboardHero } from "@/components/dashboards/RoleDashboardHero";
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
      <RoleDashboardHero
        tone="primary"
        eyebrow="Faturação"
        title="Painel de faturação"
        description="Receitas, faturas pendentes e pagamentos do dia."
        primaryAction={{ to: "/billing/invoices/new", label: "Nova fatura" }}
        secondaryAction={{ to: "/billing/invoices", label: "Todas as faturas" }}
      />

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
