import { useQuery } from "@tanstack/react-query";
import { useMemo, useState, type ReactNode } from "react";

import { DisplayDateInput } from "@/components/forms/DisplayDateInput";
import { Button, Card, CurrencyDisplay, ErrorState, SkeletonCard } from "@/design-system";
import { usePermissions } from "@/hooks/usePermissions";
import { billingService } from "@/services/billing/billing.service";
import type { OperationalBillingSummary, OperationalPeriod } from "@/types/billing";
import { displayDateToApi, apiDateToDisplay, isValidDisplayDate } from "@/utils/date";

const PERIOD_OPTIONS: { id: OperationalPeriod; label: string }[] = [
  { id: "hoje", label: "Hoje" },
  { id: "semana", label: "Esta semana" },
  { id: "mes", label: "Este mês" },
  { id: "personalizado", label: "Personalizado" },
];

function Metric({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="rounded-xl border border-border bg-surface-muted/40 px-4 py-3">
      <p className="text-xs font-medium text-text-muted">{label}</p>
      <p className="mt-1 text-lg font-semibold tabular-nums text-text">{children}</p>
    </div>
  );
}

export function ReceptionFinancialSummary() {
  const { hasPermission } = usePermissions();
  const canView = hasPermission("billing.view");

  const [periodo, setPeriodo] = useState<OperationalPeriod>("hoje");
  const [deDisplay, setDeDisplay] = useState("");
  const [ateDisplay, setAteDisplay] = useState("");
  const [appliedCustom, setAppliedCustom] = useState<{ de: string; ate: string } | null>(null);

  const queryParams = useMemo(() => {
    if (periodo !== "personalizado") {
      return { periodo };
    }
    if (!appliedCustom) return null;
    return {
      periodo: "personalizado" as const,
      data_inicio: appliedCustom.de,
      data_fim: appliedCustom.ate,
    };
  }, [periodo, appliedCustom]);

  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ["billing-resumo-operacional", queryParams],
    queryFn: () => billingService.getOperationalSummary(queryParams!),
    enabled: canView && queryParams != null,
  });

  if (!canView) return null;

  const customReady =
    isValidDisplayDate(deDisplay) &&
    isValidDisplayDate(ateDisplay) &&
    displayDateToApi(deDisplay) <= displayDateToApi(ateDisplay);

  function applyCustom() {
    if (!customReady) return;
    setAppliedCustom({
      de: displayDateToApi(deDisplay),
      ate: displayDateToApi(ateDisplay),
    });
  }

  function selectPeriod(next: OperationalPeriod) {
    setPeriodo(next);
    if (next !== "personalizado") {
      setAppliedCustom(null);
    }
  }

  return (
    <Card title="Resumo financeiro" description="Totais do balcão no período seleccionado.">
      <div className="flex flex-wrap gap-2">
        {PERIOD_OPTIONS.map((opt) => (
          <button
            key={opt.id}
            type="button"
            onClick={() => selectPeriod(opt.id)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
              periodo === opt.id
                ? "bg-primary-600 text-white"
                : "bg-surface-muted text-text hover:bg-slate-200/80 dark:hover:bg-slate-700"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {periodo === "personalizado" && (
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end">
          <div className="min-w-[10rem] flex-1">
            <DisplayDateInput label="De" value={deDisplay} onValueChange={setDeDisplay} />
          </div>
          <div className="min-w-[10rem] flex-1">
            <DisplayDateInput label="Até" value={ateDisplay} onValueChange={setAteDisplay} />
          </div>
          <Button type="button" variant="primary" disabled={!customReady} onClick={applyCustom}>
            Aplicar
          </Button>
        </div>
      )}

      {periodo === "personalizado" && !appliedCustom ? (
        <p className="mt-4 text-sm text-text-muted">Indique as datas e prima Aplicar.</p>
      ) : isLoading || isFetching ? (
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : isError ? (
        <div className="mt-4">
          <ErrorState message="Não foi possível carregar o resumo financeiro." onRetry={() => void refetch()} />
        </div>
      ) : data ? (
        <SummaryGrid data={data} />
      ) : null}
    </Card>
  );
}

function SummaryGrid({ data }: { data: OperationalBillingSummary }) {
  const inicio = apiDateToDisplay(data.periodo.data_inicio);
  const fim = apiDateToDisplay(data.periodo.data_fim);
  const periodoLabel =
    inicio === fim ? `Período: ${inicio}` : `Período: ${inicio} a ${fim}`;

  return (
    <div className="mt-4 space-y-3">
      <p className="text-xs text-text-muted">{periodoLabel}</p>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Metric label="Total faturado">
          <CurrencyDisplay value={data.total_faturado} />
        </Metric>
        <Metric label="Total recebido">
          <CurrencyDisplay value={data.total_recebido} />
        </Metric>
        <Metric label="Saldo pendente">
          <CurrencyDisplay value={data.saldo_pendente} />
        </Metric>
        <Metric label="Reduções">
          <CurrencyDisplay value={data.total_reducoes} />
        </Metric>
        <Metric label="Pagamentos">{data.numero_pagamentos}</Metric>
      </div>
    </div>
  );
}
