import { Card } from "@/design-system";
import type { BillingDashboardData } from "@/types/billing";

interface BillingDashboardCardsProps {
  data: BillingDashboardData;
}

export function BillingDashboardCards({ data }: BillingDashboardCardsProps) {
  const cards = [
    { label: "Receita hoje", value: data.indicadores.receita_hoje },
    { label: "Receita mensal", value: data.indicadores.receita_mensal },
    { label: "Faturas pendentes", value: data.indicadores.faturas_pendentes },
    { label: "Faturas pagas", value: data.indicadores.faturas_pagas },
    { label: "Pagamentos do dia", value: data.indicadores.pagamentos_do_dia },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      {cards.map((card) => (
        <Card key={card.label} title={card.label}>
          <p className="text-2xl font-bold text-primary-700">{card.value}</p>
        </Card>
      ))}
    </div>
  );
}
