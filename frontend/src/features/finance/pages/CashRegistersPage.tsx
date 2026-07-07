import { useQuery } from "@tanstack/react-query";

import { ErrorState, LoadingState } from "@/design-system";
import { CashRegisterTable } from "@/features/finance/components/CashRegisterTable";
import { FinanceSubNav } from "@/features/finance/components/FinanceSubNav";
import { financeService } from "@/services/finance/finance.service";

export function CashRegistersPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["finance-cash-registers"],
    queryFn: () => financeService.listCashRegisters(),
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Caixas</h2>
        <p className="mt-1 text-slate-600">Gestão de abertura e fecho de caixa.</p>
      </div>
      <FinanceSubNav />

      {isLoading ? (
        <LoadingState message="A carregar caixas..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar as caixas." onRetry={() => void refetch()} />
      ) : (
        <CashRegisterTable registers={data?.results ?? []} />
      )}
    </div>
  );
}
