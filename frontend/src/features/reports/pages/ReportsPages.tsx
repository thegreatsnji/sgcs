import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { ErrorState, LoadingState } from "@/design-system";
import { ChartCard } from "@/features/reports/components/ChartCard";
import { DepartmentPerformanceGrid } from "@/features/reports/components/DepartmentPerformanceGrid";
import { ExecutiveAlertsPanel } from "@/features/reports/components/ExecutiveAlertsPanel";
import { ExecutiveChartsGrid } from "@/features/reports/components/ExecutiveChartsGrid";
import { ExecutiveKpiStrip } from "@/features/reports/components/ExecutiveKpiStrip";
import { ExecutiveDashboardSkeleton } from "@/features/reports/components/ExecutiveSkeleton";
import { ExportMenu } from "@/features/reports/components/ExportMenu";
import { computeCollectionRate } from "@/features/reports/utils/executiveMetrics";
import { appointmentsService } from "@/services/appointments/appointments.service";
import { billingService } from "@/services/billing/billing.service";
import { dashboardService } from "@/services/dashboard";
import { financeService } from "@/services/finance/finance.service";
import { laboratoryService } from "@/services/laboratory";
import { notificationsService } from "@/services/notifications/notifications.service";
import { ReportCard } from "@/features/reports/components/ReportCard";
import { ReportFilter } from "@/features/reports/components/ReportFilter";
import { ReportsSubNav } from "@/features/reports/components/ReportsSubNav";
import { reportsService } from "@/services/reports/reports.service";
import type { ReportPeriod } from "@/types/reports";

interface GenericReportPageProps {
  title: string;
  subtitle: string;
  tipo: string;
  fetcher: (params: { periodo: ReportPeriod }) => Promise<{
    resumo: Record<string, number | string>;
    series?: { consultas: Array<{ data: string; valor: number }> };
  }>;
}

function GenericReportPage({ title, subtitle, tipo, fetcher }: GenericReportPageProps) {
  const [periodo, setPeriodo] = useState<ReportPeriod>("mes");
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["report", tipo, periodo],
    queryFn: () => fetcher({ periodo }),
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{title}</h2>
          <p className="mt-1 text-slate-600">{subtitle}</p>
        </div>
        <ExportMenu tipo={tipo} filters={{ periodo }} />
      </div>
      <ReportsSubNav />
      <ReportFilter periodo={periodo} onPeriodoChange={setPeriodo} />

      {isLoading ? (
        <LoadingState message="A gerar relatório..." />
      ) : isError || !data ? (
        <ErrorState message="Não foi possível carregar o relatório." onRetry={() => void refetch()} />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(data.resumo).map(([key, value]) => (
              <ReportCard key={key} title={key.replace(/_/g, " ")} value={value} />
            ))}
          </div>
          {data.series?.consultas && <ChartCard title="Consultas (série temporal)" data={data.series.consultas} />}
        </>
      )}
    </div>
  );
}

export function ReportsDashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["reports-charts"],
    queryFn: reportsService.getCharts,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Relatórios e BI</h2>
        <p className="mt-1 text-slate-600">Business Intelligence e estatísticas da clínica.</p>
      </div>
      <ReportsSubNav />
      {isLoading || !data ? (
        <LoadingState message="A carregar indicadores..." />
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          <ChartCard title="Receitas" data={data.receitas} />
          <ChartCard title="Consultas" data={data.consultas} />
          <ChartCard title="Pacientes" data={data.pacientes} />
          <ChartCard title="Laboratório" data={data.laboratorio} />
        </div>
      )}
    </div>
  );
}

export function PatientsReportPage() {
  return (
    <GenericReportPage
      title="Relatório de Pacientes"
      subtitle="Demografia e evolução de pacientes."
      tipo="patients"
      fetcher={(p) => reportsService.getPatientsReport(p)}
    />
  );
}

export function AppointmentsReportPage() {
  return (
    <GenericReportPage
      title="Relatório de Consultas"
      subtitle="Volume, médicos e tempos médios."
      tipo="appointments"
      fetcher={(p) => reportsService.getAppointmentsReport(p)}
    />
  );
}

export function LaboratoryReportPage() {
  return (
    <GenericReportPage
      title="Relatório de Laboratório"
      subtitle="Pedidos, exames e resultados."
      tipo="laboratory"
      fetcher={(p) => reportsService.getLaboratoryReport(p)}
    />
  );
}

export function BillingReportPage() {
  return (
    <GenericReportPage
      title="Relatório de Faturação"
      subtitle="Faturas, pagamentos e serviços vendidos."
      tipo="billing"
      fetcher={(p) => reportsService.getBillingReport(p)}
    />
  );
}

export function FinanceReportPage() {
  return (
    <GenericReportPage
      title="Relatório Financeiro"
      subtitle="Receitas, despesas e fluxo de caixa."
      tipo="finance"
      fetcher={(p) => reportsService.getFinanceReport(p)}
    />
  );
}

export function ExecutiveReportPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["executive-dashboard"],
    queryFn: reportsService.getExecutiveDashboard,
    refetchInterval: 120_000,
  });

  const { data: reception } = useQuery({
    queryKey: ["reception-dashboard"],
    queryFn: dashboardService.getReceptionSummary,
  });

  const { data: medical } = useQuery({
    queryKey: ["consultas-dashboard"],
    queryFn: appointmentsService.getDashboard,
  });

  const { data: laboratory } = useQuery({
    queryKey: ["laboratory-dashboard"],
    queryFn: laboratoryService.getDashboard,
  });

  const { data: billing } = useQuery({
    queryKey: ["billing-dashboard"],
    queryFn: billingService.getDashboard,
  });

  const { data: finance } = useQuery({
    queryKey: ["finance-dashboard"],
    queryFn: financeService.getDashboard,
  });

  const { data: notifications } = useQuery({
    queryKey: ["notifications-dashboard"],
    queryFn: notificationsService.getDashboard,
  });

  const { data: unread } = useQuery({
    queryKey: ["notifications-unread"],
    queryFn: notificationsService.unread,
    refetchInterval: 60_000,
  });

  const loading =
    isLoading ||
    !data ||
    !reception ||
    !medical ||
    !laboratory ||
    !billing ||
    !finance ||
    !notifications;

  const collectionRate = computeCollectionRate(
    billing?.indicadores.faturas_pagas ?? 0,
    billing?.indicadores.faturas_pendentes ?? 0,
  );

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-primary-600 via-primary-700 to-slate-900 p-6 text-white shadow-lg shadow-primary-900/20 sm:p-8">
        <p className="text-xs font-semibold tracking-widest text-primary-100 uppercase">Análise Clínica SauVida</p>
        <h1 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">Painel Executivo</h1>
        <p className="mt-2 max-w-2xl text-sm text-primary-100/90">
          Visão consolidada para direcção clínica — indicadores financeiros, operacionais e alertas em tempo real.
        </p>
      </div>

      <ReportsSubNav />

      {loading ? (
        <ExecutiveDashboardSkeleton />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar o dashboard." onRetry={() => void refetch()} />
      ) : (
        <>
          <ExecutiveKpiStrip
            patientsToday={reception.cards.attended_today}
            patientsWaiting={reception.cards.patients_waiting}
            revenueToday={billing.indicadores.receita_hoje}
            appointmentsToday={medical.indicadores.consultas_do_dia}
            appointmentsCompleted={medical.indicadores.consultas_concluidas}
            laboratoryRequests={
              medical.indicadores.pedidos_laboratorio_emitidos ??
              laboratory.indicadores.pedidos_pendentes + laboratory.indicadores.em_processamento
            }
            laboratoryPending={laboratory.resultados?.resultados_pendentes ?? laboratory.indicadores.pedidos_pendentes}
            collectionRate={collectionRate}
            paidInvoices={billing.indicadores.faturas_pagas}
            pendingInvoices={billing.indicadores.faturas_pendentes}
          />

          <div className="grid gap-4 lg:grid-cols-4">
            <div className="lg:col-span-3">
              <ExecutiveChartsGrid graficos={data.graficos} />
            </div>
            <div className="lg:col-span-1">
              <ExecutiveAlertsPanel
                pendingLabResults={laboratory.resultados?.resultados_pendentes ?? laboratory.indicadores.pedidos_pendentes}
                unpaidInvoices={billing.indicadores.faturas_pendentes}
                unreadNotifications={notifications.nao_lidas}
                notificationFailures={notifications.falhas}
                notifications={unread?.notificacoes ?? []}
              />
            </div>
          </div>

          <DepartmentPerformanceGrid
            reception={reception}
            medical={medical}
            laboratory={laboratory}
            billing={billing}
            finance={finance}
            graficos={data.graficos}
            collectionRate={collectionRate}
          />
        </>
      )}
    </div>
  );
}
