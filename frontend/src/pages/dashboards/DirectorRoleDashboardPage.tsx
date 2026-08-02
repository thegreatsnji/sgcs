import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { DepartmentPerformanceGrid } from "@/features/reports/components/DepartmentPerformanceGrid";
import { ExecutiveAlertsPanel } from "@/features/reports/components/ExecutiveAlertsPanel";
import { ExecutiveChartsGrid } from "@/features/reports/components/ExecutiveChartsGrid";
import { ExecutiveDashboardSkeleton } from "@/features/reports/components/ExecutiveSkeleton";
import { ExecutiveKpiStrip } from "@/features/reports/components/ExecutiveKpiStrip";
import { computeCollectionRate, formatCompactCurrency } from "@/features/reports/utils/executiveMetrics";
import { appointmentsService } from "@/services/appointments/appointments.service";
import { billingService } from "@/services/billing/billing.service";
import { dashboardService } from "@/services/dashboard";
import { financeService } from "@/services/finance/finance.service";
import { laboratoryService } from "@/services/laboratory";
import { notificationsService } from "@/services/notifications/notifications.service";
import { reportsService } from "@/services/reports/reports.service";
import { ErrorState, Card } from "@/design-system";

export function DirectorRoleDashboardPage() {
  const executive = useQuery({
    queryKey: ["executive-dashboard"],
    queryFn: reportsService.getExecutiveDashboard,
    refetchInterval: 120_000,
  });

  const reception = useQuery({ queryKey: ["reception-dashboard"], queryFn: dashboardService.getReceptionSummary });
  const medical = useQuery({ queryKey: ["consultas-dashboard"], queryFn: appointmentsService.getDashboard });
  const laboratory = useQuery({ queryKey: ["laboratory-dashboard"], queryFn: laboratoryService.getDashboard });
  const billing = useQuery({ queryKey: ["billing-dashboard"], queryFn: billingService.getDashboard });
  const finance = useQuery({ queryKey: ["finance-dashboard"], queryFn: financeService.getDashboard });
  const notifications = useQuery({ queryKey: ["notifications-dashboard"], queryFn: notificationsService.getDashboard });
  const unread = useQuery({ queryKey: ["notifications-unread"], queryFn: notificationsService.unread, refetchInterval: 60_000 });

  const loading =
    executive.isLoading ||
    !executive.data ||
    !reception.data ||
    !medical.data ||
    !laboratory.data ||
    !billing.data ||
    !finance.data ||
    !notifications.data;

  if (loading) return <ExecutiveDashboardSkeleton />;
  if (executive.isError) {
    return <ErrorState message="Não foi possível carregar o painel executivo." onRetry={() => void executive.refetch()} />;
  }

  const collectionRate = computeCollectionRate(
    billing.data!.indicadores.faturas_pagas,
    billing.data!.indicadores.faturas_pendentes,
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-primary-600 via-primary-700 to-slate-900 p-6 text-white shadow-lg sm:p-8">
          <p className="text-xs font-semibold tracking-widest text-primary-100 uppercase">Direcção Clínica</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">Painel Executivo</h1>
          <p className="mt-2 text-sm text-primary-100/90">Visão financeira e operacional da clínica SauVida.</p>
        </div>
        <Link to="/reports/executive" className="inline-flex h-fit items-center rounded-xl bg-white px-4 py-2.5 text-sm font-medium text-primary-700 shadow-sm ring-1 ring-slate-200 hover:bg-slate-50">
          Relatório completo →
        </Link>
      </div>

      <ExecutiveKpiStrip
        patientsToday={reception.data!.cards.attended_today}
        patientsWaiting={reception.data!.cards.patients_waiting}
        revenueToday={billing.data!.indicadores.receita_hoje}
        appointmentsToday={medical.data!.indicadores.consultas_do_dia}
        appointmentsCompleted={medical.data!.indicadores.consultas_concluidas}
        laboratoryRequests={
          medical.data!.indicadores.pedidos_laboratorio_emitidos ??
          laboratory.data!.indicadores.pedidos_pendentes + laboratory.data!.indicadores.em_processamento
        }
        laboratoryPending={laboratory.data!.resultados?.resultados_pendentes ?? laboratory.data!.indicadores.pedidos_pendentes}
        collectionRate={collectionRate}
        paidInvoices={billing.data!.indicadores.faturas_pagas}
        pendingInvoices={billing.data!.indicadores.faturas_pendentes}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card title="Receita do mês">
          <p className="text-2xl font-bold text-slate-900">{formatCompactCurrency(billing.data!.indicadores.receita_mensal)}</p>
          <p className="mt-1 text-xs text-slate-500">Acumulado no período actual</p>
        </Card>
        <Card title="Saldo em dívida">
          <p className="text-2xl font-bold text-amber-700">{billing.data!.indicadores.faturas_pendentes}</p>
          <p className="mt-1 text-xs text-slate-500">Faturas por liquidar</p>
        </Card>
        <Card title="Pagamentos hoje">
          <p className="text-2xl font-bold text-emerald-700">{billing.data!.indicadores.pagamentos_do_dia}</p>
          <p className="mt-1 text-xs text-slate-500">Movimentos confirmados</p>
        </Card>
        <Card title="Exames (lab.)">
          <p className="text-2xl font-bold text-slate-900">{laboratory.data!.indicadores.pedidos_pendentes + laboratory.data!.indicadores.em_processamento}</p>
          <p className="mt-1 text-xs text-slate-500">Pendentes + em processamento</p>
        </Card>
      </div>

      {billing.data!.servicos_mais_vendidos.length > 0 && (
        <Card title="Serviços mais utilizados">
          <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {billing.data!.servicos_mais_vendidos.slice(0, 6).map((s) => (
              <li key={s.servico} className="flex justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm">
                <span className="truncate font-medium text-slate-800">{s.servico}</span>
                <span className="shrink-0 tabular-nums text-slate-600">{s.quantidade}×</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      <div className="grid gap-4 lg:grid-cols-4">
        <div className="lg:col-span-3">
          <ExecutiveChartsGrid graficos={executive.data!.graficos} />
        </div>
        <div className="lg:col-span-1">
          <ExecutiveAlertsPanel
            pendingLabResults={laboratory.data!.resultados?.resultados_pendentes ?? laboratory.data!.indicadores.pedidos_pendentes}
            unpaidInvoices={billing.data!.indicadores.faturas_pendentes}
            unreadNotifications={notifications.data!.nao_lidas}
            notificationFailures={notifications.data!.falhas}
            notifications={unread.data?.notificacoes ?? []}
          />
        </div>
      </div>

      <DepartmentPerformanceGrid
        reception={reception.data!}
        medical={medical.data!}
        laboratory={laboratory.data!}
        billing={billing.data!}
        finance={finance.data!}
        graficos={executive.data!.graficos}
        collectionRate={collectionRate}
      />
    </div>
  );
}
