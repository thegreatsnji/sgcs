import { IconBilling, IconCalendar, IconLab, IconPatients } from "@/components/icons";
import { KpiCard } from "@/components/ui/KpiCard";
import { formatCompactCurrency } from "@/features/reports/utils/executiveMetrics";

interface ExecutiveKpiStripProps {
  patientsToday: number;
  patientsWaiting: number;
  revenueToday: number;
  appointmentsToday: number;
  appointmentsCompleted: number;
  laboratoryRequests: number;
  laboratoryPending: number;
  collectionRate: number;
  paidInvoices: number;
  pendingInvoices: number;
}

export function ExecutiveKpiStrip({
  patientsToday,
  patientsWaiting,
  revenueToday,
  appointmentsToday,
  appointmentsCompleted,
  laboratoryRequests,
  laboratoryPending,
  collectionRate,
  paidInvoices,
  pendingInvoices,
}: ExecutiveKpiStripProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
      <KpiCard
        label="Pacientes Hoje"
        value={patientsToday}
        icon={<IconPatients />}
        badge={
          patientsWaiting > 0
            ? { text: `${patientsWaiting} em espera`, variant: "warning" }
            : { text: "Fluxo normal", variant: "success" }
        }
      />
      <KpiCard
        label="Receita Hoje"
        value={formatCompactCurrency(revenueToday)}
        icon={<IconBilling />}
        badge={{ text: "Pagamentos confirmados", variant: "success" }}
      />
      <KpiCard
        label="Consultas Hoje"
        value={appointmentsToday}
        icon={<IconCalendar />}
        badge={{ text: `${appointmentsCompleted} concluídas`, variant: "info" }}
      />
      <KpiCard
        label="Pedidos Laboratório"
        value={laboratoryRequests}
        icon={<IconLab />}
        badge={
          laboratoryPending > 0
            ? { text: `${laboratoryPending} pendentes`, variant: "warning" }
            : { text: "Sem fila crítica", variant: "success" }
        }
      />
      <KpiCard
        label="Taxa de Cobrança"
        value={`${collectionRate}%`}
        icon={<IconBilling />}
        badge={{ text: `${paidInvoices} pagas · ${pendingInvoices} pendentes`, variant: "default" }}
      />
    </div>
  );
}
