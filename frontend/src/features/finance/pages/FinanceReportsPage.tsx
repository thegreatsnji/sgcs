import { useQuery } from "@tanstack/react-query";

import { Card, ErrorState, LoadingState } from "@/design-system";
import { FinanceSubNav } from "@/features/finance/components/FinanceSubNav";
import { financeService } from "@/services/finance/finance.service";

function ReportCard({ title, report }: { title: string; report: { receitas: number; despesas: number; lucro: number; pagamentos: number; periodo: string } }) {
  return (
    <Card title={title}>
      <p className="mb-3 text-sm text-slate-500">Período: {report.periodo}</p>
      <dl className="grid gap-2 text-sm sm:grid-cols-2">
        <div><dt className="text-slate-500">Receitas</dt><dd className="font-semibold text-green-700">{report.receitas} FCFA</dd></div>
        <div><dt className="text-slate-500">Despesas</dt><dd className="font-semibold text-red-700">{report.despesas} FCFA</dd></div>
        <div><dt className="text-slate-500">Lucro</dt><dd className="font-semibold">{report.lucro} FCFA</dd></div>
        <div><dt className="text-slate-500">Pagamentos</dt><dd className="font-semibold">{report.pagamentos}</dd></div>
      </dl>
    </Card>
  );
}

export function FinanceReportsPage() {
  const daily = useQuery({ queryKey: ["finance-report-daily"], queryFn: financeService.getDailyReport });
  const monthly = useQuery({ queryKey: ["finance-report-monthly"], queryFn: financeService.getMonthlyReport });

  const isLoading = daily.isLoading || monthly.isLoading;
  const isError = daily.isError || monthly.isError;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Relatórios</h2>
        <p className="mt-1 text-slate-600">Relatórios financeiros diários e mensais.</p>
      </div>
      <FinanceSubNav />

      {isLoading ? (
        <LoadingState message="A gerar relatórios..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar os relatórios." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {daily.data && <ReportCard title="Relatório diário" report={daily.data} />}
          {monthly.data && <ReportCard title="Relatório mensal" report={monthly.data} />}
        </div>
      )}
    </div>
  );
}
