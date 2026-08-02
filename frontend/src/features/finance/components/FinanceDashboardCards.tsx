import { KpiCard } from "@/components/ui/KpiCard";
import { formatFinanceCurrency } from "@/features/finance/utils/financeDashboard";
import type { FinanceDashboardData } from "@/types/finance";

export function FinanceDashboardCards({ data }: { data: FinanceDashboardData }) {
  const { indicadores } = data;

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <KpiCard
        label="Receita Hoje"
        value={formatFinanceCurrency(indicadores.receita_hoje)}
        badge={{ text: "Entradas do dia", variant: "success" }}
      />
      <KpiCard
        label="Receita Mensal"
        value={formatFinanceCurrency(indicadores.receita_mensal)}
        badge={{ text: "Acumulado", variant: "info" }}
      />
      <KpiCard
        label="Despesa Hoje"
        value={formatFinanceCurrency(indicadores.despesa_hoje)}
        badge={{ text: "Saídas do dia", variant: "warning" }}
      />
      <KpiCard
        label="Despesa Mensal"
        value={formatFinanceCurrency(indicadores.despesa_mensal)}
        badge={{ text: "Acumulado", variant: "warning" }}
      />
      <KpiCard
        label="Lucro"
        value={formatFinanceCurrency(indicadores.lucro)}
        badge={{
          text: indicadores.lucro >= 0 ? "Positivo" : "Negativo",
          variant: indicadores.lucro >= 0 ? "success" : "danger",
        }}
      />
      <KpiCard
        label="Saldo Actual"
        value={formatFinanceCurrency(indicadores.saldo_actual)}
        badge={{ text: `${indicadores.pagamentos_confirmados} pagamentos`, variant: "default" }}
      />
    </div>
  );
}
