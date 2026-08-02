import { Link } from "react-router-dom";

import { Badge, Card } from "@/design-system";
import type { Notificacao } from "@/types/notifications";

interface ExecutiveAlertsPanelProps {
  pendingLabResults: number;
  unpaidInvoices: number;
  unreadNotifications: number;
  notificationFailures: number;
  notifications: Notificacao[];
}

export function ExecutiveAlertsPanel({
  pendingLabResults,
  unpaidInvoices,
  unreadNotifications,
  notificationFailures,
  notifications,
}: ExecutiveAlertsPanelProps) {
  const alerts = [
    {
      id: "lab",
      title: "Resultados de laboratório pendentes",
      count: pendingLabResults,
      href: "/laboratory/results",
      variant: "warning" as const,
      description: "Aguardam validação ou entrega",
    },
    {
      id: "invoices",
      title: "Faturas por liquidar",
      count: unpaidInvoices,
      href: "/billing/invoices",
      variant: "danger" as const,
      description: "Faturas com saldo em aberto",
    },
    {
      id: "notifications",
      title: "Notificações do sistema",
      count: unreadNotifications,
      href: "/notifications",
      variant: "info" as const,
      description:
        notificationFailures > 0
          ? `${notificationFailures} falha(s) de envio registada(s)`
          : "Alertas e mensagens internas",
    },
  ];

  return (
    <Card title="Alertas Operacionais" className="h-full">
      <div className="space-y-3">
        {alerts.map((alert) => (
          <Link
            key={alert.id}
            to={alert.href}
            className="block rounded-xl border border-slate-200/80 bg-slate-50/50 p-4 transition hover:border-primary-200 hover:bg-primary-50/40"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="font-medium text-slate-900">{alert.title}</p>
                <p className="mt-1 text-xs text-slate-500">{alert.description}</p>
              </div>
              <Badge variant={alert.variant}>{alert.count}</Badge>
            </div>
          </Link>
        ))}
      </div>

      <div className="mt-6 border-t border-slate-100 pt-4">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-900">Últimas notificações</h3>
          <Link to="/notifications" className="text-xs font-medium text-primary-600 hover:text-primary-700">
            Ver todas
          </Link>
        </div>
        {notifications.length === 0 ? (
          <p className="text-sm text-slate-500">Sem notificações recentes.</p>
        ) : (
          <ul className="space-y-3">
            {notifications.slice(0, 5).map((item) => (
              <li key={item.id} className="rounded-lg bg-white p-3 ring-1 ring-slate-100">
                <p className="text-sm font-medium text-slate-900">{item.titulo}</p>
                <p className="mt-1 line-clamp-2 text-xs text-slate-500">{item.mensagem}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Card>
  );
}
