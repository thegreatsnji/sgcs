import { Card } from "@/design-system";
import type { ExecutiveDashboard } from "@/types/reports";

export function DashboardExecutiveCards({ data }: { data: ExecutiveDashboard }) {
  const k = data.indicadores;
  const cards = [
    { label: "Receita mensal", value: `${k.receita_mensal.toLocaleString("pt-PT")} FCFA` },
    { label: "Lucro", value: `${k.lucro.toLocaleString("pt-PT")} FCFA` },
    { label: "Pacientes novos", value: k.pacientes_novos },
    { label: "Consultas", value: k.consultas },
    { label: "Exames", value: k.exames },
    { label: "Tempo médio (min)", value: k.tempo_medio_consulta_min },
  ];
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {cards.map((c) => (
        <Card key={c.label} title={c.label}>
          <p className="text-2xl font-bold text-primary-700">{c.value}</p>
        </Card>
      ))}
    </div>
  );
}
