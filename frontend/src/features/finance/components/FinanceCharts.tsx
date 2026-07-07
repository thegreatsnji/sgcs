import { Card } from "@/design-system";

export function FinanceCharts({ topCategorias }: { topCategorias: Array<{ categoria: string; total: number }> }) {
  if (!topCategorias.length) return null;
  return (
    <Card title="Top categorias de despesa">
      <ul className="space-y-2 text-sm">
        {topCategorias.map((c) => (
          <li key={c.categoria} className="flex justify-between">
            <span>{c.categoria}</span>
            <span className="font-medium">{c.total} FCFA</span>
          </li>
        ))}
      </ul>
    </Card>
  );
}
