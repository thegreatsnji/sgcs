import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card } from "@/design-system";
import { formatFinanceCurrency, type CashFlowData } from "@/features/finance/utils/financeDashboard";
import type { FinanceReport } from "@/types/finance";

const INCOME_COLOR = "#10b981";
const EXPENSE_COLOR = "#ef4444";
const CATEGORY_COLORS = ["#2563eb", "#8b5cf6", "#f59e0b", "#ec4899", "#06b6d4", "#64748b"];

interface FinanceChartsProps {
  cashFlow: CashFlowData;
  topCategorias: Array<{ categoria: string; total: number }>;
  dailyReport?: FinanceReport;
  monthlyReport?: FinanceReport;
}

export function FinanceCharts({ cashFlow, topCategorias, dailyReport, monthlyReport }: FinanceChartsProps) {
  const cashFlowData = [
    {
      periodo: "Hoje",
      entradas: cashFlow.fluxo_diario.entradas,
      saidas: cashFlow.fluxo_diario.saidas,
      saldo: cashFlow.saldo_diario,
    },
    {
      periodo: "Mês",
      entradas: cashFlow.fluxo_mensal.entradas,
      saidas: cashFlow.fluxo_mensal.saidas,
      saldo: cashFlow.saldo_mensal,
    },
  ];

  const incomeExpenseData = [
    { name: "Hoje", receitas: cashFlow.receitas_hoje, despesas: cashFlow.despesas_hoje },
    { name: "Mês", receitas: cashFlow.receitas_mes, despesas: cashFlow.despesas_mes },
  ];

  const categoryData = topCategorias.slice(0, 8).map((c) => ({
    name: c.categoria.length > 16 ? `${c.categoria.slice(0, 16)}…` : c.categoria,
    total: c.total,
  }));

  const comparisonData = [
    dailyReport && {
      periodo: "Diário",
      receitas: dailyReport.receitas,
      despesas: dailyReport.despesas,
      lucro: dailyReport.lucro,
    },
    monthlyReport && {
      periodo: "Mensal",
      receitas: monthlyReport.receitas,
      despesas: monthlyReport.despesas,
      lucro: monthlyReport.lucro,
    },
  ].filter(Boolean) as Array<{ periodo: string; receitas: number; despesas: number; lucro: number }>;

  return (
    <div className="space-y-4">
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Fluxo de caixa">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={cashFlowData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="periodo" tick={{ fontSize: 12, fill: "#64748b" }} />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(value: number) => formatFinanceCurrency(value)}
                  contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0" }}
                />
                <Legend />
                <Bar dataKey="entradas" name="Entradas" fill={INCOME_COLOR} radius={[6, 6, 0, 0]} />
                <Bar dataKey="saidas" name="Saídas" fill={EXPENSE_COLOR} radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <dl className="mt-4 grid grid-cols-2 gap-3 border-t border-slate-100 pt-4 text-sm">
            <div>
              <dt className="text-slate-500">Saldo diário</dt>
              <dd className={`font-semibold ${cashFlow.saldo_diario >= 0 ? "text-green-700" : "text-red-700"}`}>
                {formatFinanceCurrency(cashFlow.saldo_diario)}
              </dd>
            </div>
            <div>
              <dt className="text-slate-500">Saldo mensal</dt>
              <dd className={`font-semibold ${cashFlow.saldo_mensal >= 0 ? "text-green-700" : "text-red-700"}`}>
                {formatFinanceCurrency(cashFlow.saldo_mensal)}
              </dd>
            </div>
          </dl>
        </Card>

        <Card title="Receitas vs Despesas">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={incomeExpenseData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#64748b" }} />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(value: number) => formatFinanceCurrency(value)}
                  contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0" }}
                />
                <Legend />
                <Bar dataKey="receitas" name="Receitas" fill={INCOME_COLOR} radius={[6, 6, 0, 0]} />
                <Bar dataKey="despesas" name="Despesas" fill={EXPENSE_COLOR} radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Categorias de despesa">
          {categoryData.length === 0 ? (
            <p className="py-8 text-center text-sm text-slate-500">Sem despesas por categoria.</p>
          ) : (
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryData} layout="vertical" margin={{ top: 8, right: 16, left: 8, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 11, fill: "#64748b" }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                  <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 11, fill: "#64748b" }} />
                  <Tooltip
                    formatter={(value: number) => formatFinanceCurrency(value)}
                    contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0" }}
                  />
                  <Bar dataKey="total" name="Total" radius={[0, 6, 6, 0]}>
                    {categoryData.map((_, index) => (
                      <Cell key={index} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>

        <Card title="Comparação mensal">
          {comparisonData.length === 0 ? (
            <p className="py-8 text-center text-sm text-slate-500">Relatórios indisponíveis.</p>
          ) : (
            <>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={comparisonData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis dataKey="periodo" tick={{ fontSize: 12, fill: "#64748b" }} />
                    <YAxis tick={{ fontSize: 11, fill: "#64748b" }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                    <Tooltip
                      formatter={(value: number) => formatFinanceCurrency(value)}
                      contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0" }}
                    />
                    <Legend />
                    <Bar dataKey="receitas" name="Receitas" fill={INCOME_COLOR} radius={[6, 6, 0, 0]} />
                    <Bar dataKey="despesas" name="Despesas" fill={EXPENSE_COLOR} radius={[6, 6, 0, 0]} />
                    <Bar dataKey="lucro" name="Lucro" fill="#2563eb" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <dl className="mt-4 grid gap-3 border-t border-slate-100 pt-4 text-sm sm:grid-cols-2">
                {comparisonData.map((row) => (
                  <div key={row.periodo} className="rounded-xl bg-slate-50 p-3">
                    <dt className="font-medium text-slate-700">{row.periodo}</dt>
                    <dd className="mt-1 text-xs text-slate-500">
                      Lucro: <span className={row.lucro >= 0 ? "font-semibold text-green-700" : "font-semibold text-red-700"}>
                        {formatFinanceCurrency(row.lucro)}
                      </span>
                    </dd>
                  </div>
                ))}
              </dl>
            </>
          )}
        </Card>
      </div>
    </div>
  );
}
