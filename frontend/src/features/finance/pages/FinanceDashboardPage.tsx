import { useQuery } from "@tanstack/react-query";

import { ErrorState } from "@/design-system";
import { FinanceCharts } from "@/features/finance/components/FinanceCharts";
import { FinanceDashboardCards } from "@/features/finance/components/FinanceDashboardCards";
import { FinanceDashboardSkeleton } from "@/features/finance/components/FinanceSkeleton";
import { FinanceSubNav } from "@/features/finance/components/FinanceSubNav";
import { parseCashFlow } from "@/features/finance/utils/financeDashboard";
import { financeService } from "@/services/finance/finance.service";

export function FinanceDashboardPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["finance-dashboard"],
    queryFn: financeService.getDashboard,
    refetchInterval: 60_000,
  });

  const { data: dailyReport } = useQuery({
    queryKey: ["finance-report-daily"],
    queryFn: financeService.getDailyReport,
  });

  const { data: monthlyReport } = useQuery({
    queryKey: ["finance-report-monthly"],
    queryFn: financeService.getMonthlyReport,
  });

  if (isLoading || !data) return <FinanceDashboardSkeleton />;
  if (isError) return <ErrorState message="Não foi possível carregar o painel financeiro." onRetry={() => void refetch()} />;

  const cashFlow = parseCashFlow(data.fluxo_caixa);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Financeiro</h1>
        <p className="mt-1 text-slate-500">
          Contabilidade executiva — fluxo de caixa, despesas e comparação de períodos.
        </p>
      </div>

      <FinanceSubNav />
      <FinanceDashboardCards data={data} />

      <FinanceCharts
        cashFlow={cashFlow}
        topCategorias={data.top_categorias}
        dailyReport={dailyReport}
        monthlyReport={monthlyReport}
      />
    </div>
  );
}
