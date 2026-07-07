import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Card, ErrorState, LoadingState } from "@/design-system";
import { ChartCard } from "@/features/reports/components/ChartCard";
import { DashboardExecutiveCards } from "@/features/reports/components/DashboardExecutiveCards";
import { ExportMenu } from "@/features/reports/components/ExportMenu";
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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Dashboard Executivo</h2>
        <p className="mt-1 text-slate-600">Visão consolidada para a direção clínica.</p>
      </div>
      <ReportsSubNav />
      {isLoading || !data ? (
        <LoadingState message="A carregar dashboard executivo..." />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar o dashboard." onRetry={() => void refetch()} />
      ) : (
        <>
          <DashboardExecutiveCards data={data} />
          <div className="grid gap-4 lg:grid-cols-2">
            <Card title="Top médicos">
              <ul className="space-y-1 text-sm">
                {data.top_medicos.map((m) => (
                  <li key={m.medico} className="flex justify-between">
                    <span>{m.medico}</span>
                    <span>{m.total}</span>
                  </li>
                ))}
              </ul>
            </Card>
            <Card title="Top serviços">
              <ul className="space-y-1 text-sm">
                {data.top_servicos.map((s) => (
                  <li key={s.nome} className="flex justify-between">
                    <span>{s.nome}</span>
                    <span>{s.quantidade}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </div>
          <ChartCard title="Receitas" data={data.graficos.receitas} />
        </>
      )}
    </div>
  );
}
