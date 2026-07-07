import { Card } from "@/design-system";
import type { FinanceDashboardData } from "@/types/finance";

export function FinanceDashboardCards({ data }: { data: FinanceDashboardData }) {
  const cards = [
    { label: "Receita hoje", value: data.indicadores.receita_hoje },
    { label: "Receita mensal", value: data.indicadores.receita_mensal },
    { label: "Despesa hoje", value: data.indicadores.despesa_hoje },
    { label: "Despesa mensal", value: data.indicadores.despesa_mensal },
    { label: "Lucro", value: data.indicadores.lucro },
    { label: "Saldo actual", value: data.indicadores.saldo_actual },
  ];
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {cards.map((c) => (
        <Card key={c.label} title={c.label}>
          <p className="text-2xl font-bold text-primary-700">
            {typeof c.value === "number" ? `${c.value.toLocaleString("pt-PT")} FCFA` : c.value}
          </p>
        </Card>
      ))}
    </div>
  );
}
