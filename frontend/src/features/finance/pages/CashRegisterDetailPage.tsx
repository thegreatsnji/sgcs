import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { Badge, Button, Card, ErrorState, LoadingState } from "@/design-system";
import { CashSummary } from "@/features/finance/components/CashSummary";
import { FinanceSubNav } from "@/features/finance/components/FinanceSubNav";
import { financeService } from "@/services/finance/finance.service";
import { formatDisplayDateTime } from "@/utils/date";

export function CashRegisterDetailPage() {
  const { id } = useParams<{ id: string }>();
  const caixaId = Number(id);
  const queryClient = useQueryClient();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["finance-cash-register", caixaId],
    queryFn: () => financeService.getCashRegister(caixaId),
    enabled: Number.isFinite(caixaId),
  });

  const openMutation = useMutation({
    mutationFn: (saldo: number) => financeService.openCashRegister(caixaId, saldo),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["finance-cash-register", caixaId] });
      void queryClient.invalidateQueries({ queryKey: ["finance-cash-registers"] });
    },
  });

  const closeMutation = useMutation({
    mutationFn: () => financeService.closeCashRegister(caixaId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["finance-cash-register", caixaId] });
      void queryClient.invalidateQueries({ queryKey: ["finance-cash-registers"] });
    },
  });

  if (isLoading) return <LoadingState message="A carregar caixa..." />;
  if (isError || !data) return <ErrorState message="Caixa não encontrada." onRetry={() => void refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">{data.nome}</h2>
        <p className="mt-1 text-slate-600">Código: {data.codigo}</p>
      </div>
      <FinanceSubNav />

      <Card title="Estado">
        <div className="flex flex-wrap items-center gap-4">
          <Badge>{data.estado}</Badge>
          <span className="text-sm text-slate-600">Saldo actual: <strong>{data.saldo_actual} FCFA</strong></span>
          {data.data_abertura && (
            <span className="text-sm text-slate-500">Aberto em {formatDisplayDateTime(data.data_abertura)}</span>
          )}
        </div>
      </Card>

      <CashSummary
        entradas={Number(data.saldo_actual)}
        saidas={0}
        saldo={Number(data.saldo_actual)}
      />

      <div className="flex flex-wrap gap-2">
        {data.estado === "FECHADO" && (
          <Button
            variant="primary"
            disabled={openMutation.isPending}
            onClick={() => openMutation.mutate(0)}
          >
            Abrir caixa
          </Button>
        )}
        {data.estado === "ABERTO" && (
          <Button
            variant="secondary"
            disabled={closeMutation.isPending}
            onClick={() => closeMutation.mutate()}
          >
            Fechar caixa
          </Button>
        )}
      </div>
    </div>
  );
}
