import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card } from "@/design-system";
import { computeSeriesTrend, formatCompactCurrency, toChartPoints } from "@/features/reports/utils/executiveMetrics";
import type { ChartSeries } from "@/types/reports";

const CHART_CONFIG = [
  { key: "receitas" as const, title: "Tendência de Receita", color: "#2563eb" },
  { key: "pacientes" as const, title: "Crescimento de Pacientes", color: "#10b981" },
  { key: "consultas" as const, title: "Tendência de Consultas", color: "#8b5cf6" },
  { key: "laboratorio" as const, title: "Actividade Laboratorial", color: "#f59e0b" },
];

interface ExecutiveChartsGridProps {
  graficos: ChartSeries;
}

function ExecutiveChart({
  title,
  color,
  series,
}: {
  title: string;
  color: string;
  series: Array<{ data: string; valor: number }>;
}) {
  const data = toChartPoints(series);
  const trend = computeSeriesTrend(series);

  return (
    <Card title={title}>
      <div className="mb-3 flex items-center justify-between">
        <p className={`text-xs font-medium ${trend.positive ? "text-green-600" : "text-red-600"}`}>{trend.label}</p>
        {data.length > 0 && (
          <p className="text-xs text-slate-500">
            Último: {typeof data[data.length - 1]?.value === "number" && data[data.length - 1].value >= 1000
              ? formatCompactCurrency(data[data.length - 1].value)
              : data[data.length - 1]?.value}
          </p>
        )}
      </div>
      {data.length === 0 ? (
        <p className="flex h-48 items-center justify-center text-sm text-slate-500">Sem dados disponíveis.</p>
      ) : (
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
              <defs>
                <linearGradient id={`grad-${title}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.35} />
                  <stop offset="100%" stopColor={color} stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} width={36} />
              <Tooltip
                contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0", boxShadow: "0 4px 12px rgb(15 23 42 / 0.08)" }}
                formatter={(value: number) => [value >= 1000 ? formatCompactCurrency(value) : value, title]}
              />
              <Area type="monotone" dataKey="value" stroke={color} strokeWidth={2} fill={`url(#grad-${title})`} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}

export function ExecutiveChartsGrid({ graficos }: ExecutiveChartsGridProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {CHART_CONFIG.map((chart) => (
        <ExecutiveChart
          key={chart.key}
          title={chart.title}
          color={chart.color}
          series={graficos[chart.key] ?? []}
        />
      ))}
    </div>
  );
}
