import { useQuery } from "@tanstack/react-query";

import { ErrorState, LoadingState } from "@/design-system";
import { CashMovementTable } from "@/features/finance/components/CashMovementTable";
import { FinanceSubNav } from "@/features/finance/components/FinanceSubNav";
import { financeService } from "@/services/finance/finance.service";

export function CashMovementsPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["finance-movements"],
    queryFn: () => financeService.listMovements(),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Movimentos</h2>
        <p className="mt-1 text-slate-600">Histórico de entradas, saídas e transferências.</p>
      </div>
      <FinanceSubNav />

      {isLoading ? (
        <LoadingState message="A carregar movimentos..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar os movimentos." onRetry={() => void refetch()} />
      ) : (
        <CashMovementTable movements={data?.results ?? []} />
      )}
    </div>
  );
}
