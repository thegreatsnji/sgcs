import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { PillSubNav } from "@/components/layout/PillSubNav";
import { UI_COPY } from "@/constants/uiCopy";
import { Card, LoadingState } from "@/design-system";
import { NotificationFilters } from "@/features/notifications/components/NotificationFilters";
import { NotificationPreferencesForm } from "@/features/notifications/components/NotificationPreferencesForm";
import { NotificationTable } from "@/features/notifications/components/NotificationTable";
import { notificationsService } from "@/services/notifications/notifications.service";
import type { PreferenciaNotificacao } from "@/types/notifications";

function NotificationsSubNav() {
  const tabs = [
    { to: "/notifications", label: UI_COPY.nav.center, end: true },
    { to: "/notifications/history", label: UI_COPY.nav.history },
    { to: "/notifications/templates", label: UI_COPY.nav.templates },
    { to: "/notifications/preferences", label: UI_COPY.nav.preferences },
  ];
  return <PillSubNav tabs={tabs} ariaLabel="Navegação de notificações" />;
}

export function NotificationsDashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["notifications-dashboard"],
    queryFn: notificationsService.getDashboard,
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Notificações</h2>
      <NotificationsSubNav />
      {isLoading ? (
        <LoadingState />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Card title="Total">{data?.total ?? 0}</Card>
          <Card title="Não lidas">{data?.nao_lidas ?? 0}</Card>
          <Card title="E-mails hoje">{data?.emails_hoje ?? 0}</Card>
          <Card title="SMS hoje">{data?.sms_hoje ?? 0}</Card>
          <Card title="Falhas">{data?.falhas ?? 0}</Card>
          <Card title="Fila pendente">{data?.fila_pendente ?? 0}</Card>
        </div>
      )}
    </div>
  );
}

export function NotificationCenterPage() {
  const queryClient = useQueryClient();
  const [filtro, setFiltro] = useState("todas");
  const { data: dashboard } = useQuery({
    queryKey: ["notifications-dashboard"],
    queryFn: notificationsService.getDashboard,
  });
  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: notificationsService.list,
  });

  const notificacoes = useMemo(() => {
    const lista = data?.results ?? [];
    if (filtro === "nao_lidas") return lista.filter((n) => !n.lida);
    if (filtro === "lidas") return lista.filter((n) => n.lida);
    if (filtro === "urgente") return lista.filter((n) => n.tipo === "URGENTE");
    return lista;
  }, [data, filtro]);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Centro de notificações</h2>
      <NotificationsSubNav />
      <div className="grid gap-4 sm:grid-cols-3">
        <Card title="Não lidas">{dashboard?.nao_lidas ?? 0}</Card>
        <Card title="E-mails hoje">{dashboard?.emails_hoje ?? 0}</Card>
        <Card title="Fila pendente">{dashboard?.fila_pendente ?? 0}</Card>
      </div>
      <NotificationFilters filtro={filtro} onChange={setFiltro} />
      {isLoading ? (
        <LoadingState />
      ) : (
        <Card title="Lista">
          <NotificationTable
            notificacoes={notificacoes}
            onRead={(id) =>
              void notificationsService.markRead(id).then(() =>
                queryClient.invalidateQueries({ queryKey: ["notifications"] }),
              )
            }
          />
        </Card>
      )}
    </div>
  );
}

export function EmailHistoryPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["email-history"],
    queryFn: notificationsService.emailHistory,
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Histórico de e-mails</h2>
      <NotificationsSubNav />
      {isLoading ? (
        <LoadingState />
      ) : (
        <Card title="Envios recentes">
          <ul className="space-y-2 text-sm">
            {(data ?? []).map((item, i) => (
              <li key={i} className="rounded border border-slate-100 px-3 py-2">
                {(item as { destinatario?: string }).destinatario} — {(item as { estado?: string }).estado}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}

export function SMSHistoryPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["sms-history"],
    queryFn: notificationsService.smsHistory,
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Histórico SMS</h2>
      <NotificationsSubNav />
      {isLoading ? (
        <LoadingState />
      ) : (
        <Card title="Envios recentes">
          <ul className="space-y-2 text-sm">
            {(data ?? []).map((item, i) => (
              <li key={i} className="rounded border border-slate-100 px-3 py-2">
                {(item as { telefone?: string }).telefone} — {(item as { estado?: string }).estado}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}

export function TemplatesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["email-templates"],
    queryFn: notificationsService.listEmailTemplates,
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Modelos de comunicação</h2>
      <NotificationsSubNav />
      {isLoading ? (
        <LoadingState />
      ) : (
        <Card title="Modelos de e-mail">
          <ul className="space-y-2 text-sm">
            {data?.results.map((t) => (
              <li key={t.id} className="rounded border border-slate-100 px-3 py-2">
                <strong>{t.nome}</strong> — {t.codigo}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}

export function PreferencesPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["notification-preferences"],
    queryFn: notificationsService.getPreferences,
  });
  const mutation = useMutation({
    mutationFn: notificationsService.updatePreferences,
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["notification-preferences"] }),
  });

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Preferências</h2>
      <NotificationsSubNav />
      {isLoading || !data ? (
        <LoadingState />
      ) : (
        <Card title="Configurar notificações">
          <NotificationPreferencesForm
            preferencias={data}
            onSubmit={(v: Partial<PreferenciaNotificacao>) => mutation.mutate(v)}
            isPending={mutation.isPending}
          />
        </Card>
      )}
    </div>
  );
}
