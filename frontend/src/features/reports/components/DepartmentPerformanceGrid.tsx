import { Link } from "react-router-dom";

import { clampProgress, computeSeriesTrend, formatCompactCurrency } from "@/features/reports/utils/executiveMetrics";
import type { BillingDashboardData } from "@/types/billing";
import type { ConsultasDashboardData } from "@/types/appointment";
import type { FinanceDashboardData } from "@/types/finance";
import type { LaboratoryDashboardData } from "@/types/laboratory";
import type { ChartSeries } from "@/types/reports";
import type { ReceptionDashboardData } from "@/types/reception";

interface DepartmentPerformanceGridProps {
  reception: ReceptionDashboardData;
  medical: ConsultasDashboardData;
  laboratory: LaboratoryDashboardData;
  billing: BillingDashboardData;
  finance: FinanceDashboardData;
  graficos: ChartSeries;
  collectionRate: number;
}

interface DepartmentCardProps {
  name: string;
  href: string;
  kpi: string;
  kpiLabel: string;
  trend: string;
  trendPositive: boolean;
  progress: number;
  progressLabel: string;
  accent: string;
}

function DepartmentCard({
  name,
  href,
  kpi,
  kpiLabel,
  trend,
  trendPositive,
  progress,
  progressLabel,
  accent,
}: DepartmentCardProps) {
  return (
    <Link
      to={href}
      className="group rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm transition hover:border-primary-200 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase">{name}</p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-slate-900">{kpi}</p>
          <p className="mt-1 text-xs text-slate-500">{kpiLabel}</p>
        </div>
        <span className={`rounded-lg px-2 py-1 text-xs font-semibold ${accent}`}>Ver módulo →</span>
      </div>
      <p className={`mt-4 text-xs font-medium ${trendPositive ? "text-green-600" : "text-red-600"}`}>{trend}</p>
      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>{progressLabel}</span>
          <span className="font-semibold text-slate-700">{progress}%</span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-primary-600 transition-all group-hover:bg-primary-700"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </Link>
  );
}

export function DepartmentPerformanceGrid({
  reception,
  medical,
  laboratory,
  billing,
  finance,
  graficos,
  collectionRate,
}: DepartmentPerformanceGridProps) {
  const receptionTotal = reception.cards.attended_today + reception.cards.patients_waiting;
  const receptionProgress = clampProgress(
    receptionTotal > 0 ? (reception.cards.attended_today / receptionTotal) * 100 : 0,
  );

  const medicalProgress = clampProgress(
    medical.indicadores.consultas_do_dia > 0
      ? (medical.indicadores.consultas_concluidas / medical.indicadores.consultas_do_dia) * 100
      : 0,
  );

  const labTotal =
    laboratory.indicadores.pedidos_pendentes +
    laboratory.indicadores.em_processamento +
    laboratory.indicadores.concluidos_hoje;
  const labProgress = clampProgress(
    labTotal > 0 ? (laboratory.indicadores.concluidos_hoje / labTotal) * 100 : 0,
  );

  const financeProgress = clampProgress(
    finance.indicadores.receita_mensal > 0
      ? (finance.indicadores.lucro / finance.indicadores.receita_mensal) * 100
      : finance.indicadores.lucro >= 0
        ? 100
        : 0,
  );

  const receptionTrend = computeSeriesTrend(graficos.pacientes);
  const medicalTrend = computeSeriesTrend(graficos.consultas);
  const labTrend = computeSeriesTrend(graficos.laboratorio);
  const billingTrend = computeSeriesTrend(graficos.receitas);
  const financeTrend = computeSeriesTrend(graficos.pagamentos);

  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Desempenho por Departamento</h2>
        <p className="mt-1 text-sm text-slate-500">KPIs, tendências e progresso operacional em tempo real.</p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <DepartmentCard
          name="Receção"
          href="/reception"
          kpi={String(reception.cards.attended_today)}
          kpiLabel={`${reception.cards.patients_waiting} em espera · ${reception.cards.average_wait_minutes} min médio`}
          trend={receptionTrend.label}
          trendPositive={receptionTrend.positive}
          progress={receptionProgress}
          progressLabel="Taxa de atendimento"
          accent="bg-blue-50 text-blue-700"
        />
        <DepartmentCard
          name="Médico"
          href="/appointments"
          kpi={String(medical.indicadores.consultas_concluidas)}
          kpiLabel={`${medical.indicadores.consultas_do_dia} agendadas · ${medical.indicadores.medicos_em_servico} médicos activos`}
          trend={medicalTrend.label}
          trendPositive={medicalTrend.positive}
          progress={medicalProgress}
          progressLabel="Consultas concluídas"
          accent="bg-violet-50 text-violet-700"
        />
        <DepartmentCard
          name="Laboratório"
          href="/laboratory"
          kpi={String(laboratory.indicadores.em_processamento)}
          kpiLabel={`${laboratory.indicadores.pedidos_pendentes} pendentes · ${laboratory.indicadores.concluidos_hoje} hoje`}
          trend={labTrend.label}
          trendPositive={labTrend.positive}
          progress={labProgress}
          progressLabel="Pedidos concluídos"
          accent="bg-amber-50 text-amber-700"
        />
        <DepartmentCard
          name="Faturação"
          href="/billing"
          kpi={formatCompactCurrency(billing.indicadores.receita_hoje)}
          kpiLabel={`${billing.indicadores.faturas_pagas} pagas · ${billing.indicadores.faturas_pendentes} pendentes`}
          trend={billingTrend.label}
          trendPositive={billingTrend.positive}
          progress={collectionRate}
          progressLabel="Taxa de cobrança"
          accent="bg-emerald-50 text-emerald-700"
        />
        <DepartmentCard
          name="Financeiro"
          href="/finance"
          kpi={formatCompactCurrency(finance.indicadores.lucro)}
          kpiLabel={`Saldo ${formatCompactCurrency(finance.indicadores.saldo_actual)}`}
          trend={financeTrend.label}
          trendPositive={financeTrend.positive}
          progress={financeProgress}
          progressLabel="Margem operacional"
          accent="bg-slate-100 text-slate-700"
        />
      </div>
    </section>
  );
}
