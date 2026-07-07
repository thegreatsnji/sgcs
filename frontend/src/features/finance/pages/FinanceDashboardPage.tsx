import { useQuery } from "@tanstack/react-query";

import { Card, ErrorState, LoadingState } from "@/design-system";
import { FinanceCharts } from "@/features/finance/components/FinanceCharts";
import { FinanceDashboardCards } from "@/features/finance/components/FinanceDashboardCards";
import { FinanceSubNav } from "@/features/finance/components/FinanceSubNav";
import { financeService } from "@/services/finance/finance.service";

export function FinanceDashboardPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["finance-dashboard"],
    queryFn: financeService.getDashboard,
    refetchInterval: 60_000,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Financeiro</h2>
        <p className="mt-1 text-slate-600">Painel de tesouraria e indicadores financeiros.</p>
      </div>
      <FinanceSubNav />

      {isLoading || !data ? (
        <LoadingState message="A carregar indicadores..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar o painel financeiro." onRetry={() => void refetch()} />
      ) : (
        <>
          <FinanceDashboardCards data={data} />
          <FinanceCharts topCategorias={data.top_categorias} />
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
    </div>
  );
}
