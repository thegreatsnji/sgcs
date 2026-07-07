import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { Button, ErrorState, LoadingState } from "@/design-system";
import { ExpenseTable } from "@/features/finance/components/ExpenseTable";
import { FinanceSubNav } from "@/features/finance/components/FinanceSubNav";
import { financeService } from "@/services/finance/finance.service";

export function ExpensesPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["finance-expenses"],
    queryFn: () => financeService.listExpenses(),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Despesas</h2>
          <p className="mt-1 text-slate-600">Registo e aprovação de despesas da clínica.</p>
        </div>
        <Link to="/finance/expenses/new">
          <Button variant="primary">Nova despesa</Button>
        </Link>
      </div>
      <FinanceSubNav />

      {isLoading ? (
        <LoadingState message="A carregar despesas..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar as despesas." onRetry={() => void refetch()} />
      ) : (
        <ExpenseTable expenses={data?.results ?? []} />
      )}
    </div>
  );
}
