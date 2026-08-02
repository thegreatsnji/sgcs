import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card } from "@/design-system";
import { METODO_PAGAMENTO_LABEL, formatCurrency } from "@/features/billing/utils/formatBilling";
import type { Payment } from "@/types/billing";

const CHART_COLORS = ["#2563eb", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4"];

interface BillingChartsProps {
  revenueTrend: Array<{ data: string; valor: number }>;
  services: Array<{ servico: string; quantidade: number }>;
  payments: Payment[];
}

function formatChartDate(iso: string) {
  const [, month, day] = iso.split("-");
  return `${day}/${month}`;
}

export function BillingCharts({ revenueTrend, services, payments }: BillingChartsProps) {
  const trendData = useMemo(
    () =>
      revenueTrend.slice(-14).map((point) => ({
        name: formatChartDate(point.data),
        receita: point.valor,
      })),
    [revenueTrend],
  );

  const serviceData = useMemo(
    () =>
      services.slice(0, 8).map((s) => ({
        name: s.servico.length > 18 ? `${s.servico.slice(0, 18)}…` : s.servico,
        quantidade: s.quantidade,
      })),
    [services],
  );

  const paymentMethods = useMemo(() => {
    const totals = new Map<string, number>();
    for (const payment of payments) {
      const label = METODO_PAGAMENTO_LABEL[payment.metodo_pagamento] ?? payment.metodo_pagamento;
      totals.set(label, (totals.get(label) ?? 0) + Number(payment.valor));
    }
    return Array.from(totals.entries()).map(([name, value]) => ({ name, value }));
  }, [payments]);

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Card title="Tendência de receita" className="lg:col-span-2">
        {trendData.length === 0 ? (
          <p className="py-8 text-center text-sm text-slate-500">Sem dados de receita disponíveis.</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748b" }} />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(value: number) => [formatCurrency(value), "Receita"]}
                  contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0" }}
                />
                <Line type="monotone" dataKey="receita" stroke="#2563eb" strokeWidth={2.5} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>

      <Card title="Métodos de pagamento">
        {paymentMethods.length === 0 ? (
          <p className="py-8 text-center text-sm text-slate-500">Sem pagamentos registados.</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={paymentMethods}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={48}
                  outerRadius={80}
                  paddingAngle={2}
                >
                  {paymentMethods.map((_, index) => (
                    <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
              </PieChart>
            </ResponsiveContainer>
            <ul className="mt-2 space-y-1 text-xs text-slate-600">
              {paymentMethods.map((m, i) => (
                <li key={m.name} className="flex items-center justify-between gap-2">
                  <span className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full" style={{ background: CHART_COLORS[i % CHART_COLORS.length] }} />
                    {m.name}
                  </span>
                  <span className="font-medium">{formatCurrency(m.value)}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </Card>

      <Card title="Desempenho por serviço" className="lg:col-span-3">
        {serviceData.length === 0 ? (
          <p className="py-8 text-center text-sm text-slate-500">Sem dados de serviços.</p>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={serviceData} margin={{ top: 8, right: 8, left: 0, bottom: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748b" }} angle={-20} textAnchor="end" height={48} />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} allowDecimals={false} />
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0" }} />
                <Bar dataKey="quantidade" name="Quantidade" radius={[6, 6, 0, 0]}>
                  {serviceData.map((_, index) => (
                    <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </Card>
    </div>
  );
}
