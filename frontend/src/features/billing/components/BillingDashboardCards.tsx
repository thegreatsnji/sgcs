import { KpiCard } from "@/components/ui/KpiCard";
import { formatCurrency } from "@/features/billing/utils/formatBilling";
import type { BillingDashboardData } from "@/types/billing";

interface BillingDashboardCardsProps {
  data: BillingDashboardData;
}

export function BillingDashboardCards({ data }: BillingDashboardCardsProps) {
  const { indicadores } = data;

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
      <KpiCard
        label="Receita Hoje"
        value={formatCurrency(indicadores.receita_hoje)}
        badge={{ text: "Pagamentos confirmados", variant: "success" }}
      />
      <KpiCard
        label="Receita do Mês"
        value={formatCurrency(indicadores.receita_mensal)}
        badge={{ text: "Acumulado mensal", variant: "info" }}
      />
      <KpiCard
        label="Faturas Pendentes"
        value={indicadores.faturas_pendentes}
        badge={{ text: "Aguardam pagamento", variant: "warning" }}
      />
      <KpiCard
        label="Faturas Pagas"
        value={indicadores.faturas_pagas}
        badge={{ text: "Liquidadas", variant: "success" }}
      />
      <KpiCard
        label="Pagamentos Hoje"
        value={formatCurrency(indicadores.pagamentos_do_dia)}
        badge={{ text: `${indicadores.faturas_emitidas_hoje} emitidas hoje`, variant: "default" }}
      />
    </div>
  );
}
