import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { IconPatients, IconSettings } from "@/components/icons";
import { KpiCard } from "@/components/ui/KpiCard";
import { Card, EmptyState, SkeletonCard } from "@/design-system";
import { ROLE_LABELS } from "@/constants/roles";
import { dashboardService } from "@/services/dashboard";
import type { AdminDashboardData } from "@/types/user-management";

export function AdminDashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: dashboardService.getAdminSummary,
  });

  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <div>
          <div className="h-8 w-64 animate-pulse rounded-lg bg-slate-200" />
          <div className="mt-2 h-4 w-48 animate-pulse rounded-lg bg-slate-200" />
        </div>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  const primaryKpis = [
    {
      label: "Total de Utilizadores",
      value: data.cards.total_users,
      badge: { text: `${data.cards.active_users} activos`, variant: "success" as const },
      icon: <IconSettings />,
    },
    {
      label: "Sessões Activas",
      value: data.cards.active_sessions,
      badge: { text: "Agora", variant: "info" as const },
    },
    {
      label: "Total de Pacientes",
      value: data.cards.total_patients,
      badge: { text: `+${data.cards.new_patients_week} esta semana`, variant: "success" as const },
      icon: <IconPatients />,
    },
    {
      label: "Novos Utilizadores",
      value: data.cards.new_users_week,
      badge: { text: "Últimos 7 dias", variant: "default" as const },
    },
    {
      label: "Utilizadores Inactivos",
      value: data.cards.inactive_users,
      badge:
        data.cards.inactive_users > 0
          ? { text: "Rever contas", variant: "warning" as const }
          : { text: "Tudo activo", variant: "success" as const },
    },
    {
      label: "Pacientes Inactivos",
      value: data.cards.inactive_patients,
      badge: { text: "Cadastro", variant: "default" as const },
      icon: <IconPatients />,
    },
  ];

  const roleChartData = data.users_by_role.map((item: { role: string; count: number }) => ({
    name: ROLE_LABELS[item.role] ?? item.role,
    total: item.count,
  }));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
          Painel Administrativo
        </h1>
        <p className="mt-1 text-slate-500">Visão geral da gestão de utilizadores e sistema</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {primaryKpis.map((card) => (
          <KpiCard key={card.label} {...card} />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Utilizadores por Perfil">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={roleChartData} barSize={28}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    borderRadius: "12px",
                    border: "1px solid #e2e8f0",
                    boxShadow: "0 4px 12px rgb(15 23 42 / 0.08)",
                  }}
                />
                <Bar dataKey="total" fill="#2563eb" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Logins (últimos 7 dias)">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.logins_by_day} barSize={28}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    borderRadius: "12px",
                    border: "1px solid #e2e8f0",
                    boxShadow: "0 4px 12px rgb(15 23 42 / 0.08)",
                  }}
                />
                <Bar dataKey="count" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card title="Últimos Logins">
          {data.recent_logins.length === 0 ? (
            <EmptyState title="Sem logins" description="Nenhum acesso recente registado." />
          ) : (
            <ul className="divide-y divide-slate-100">
              {data.recent_logins.map((item: AdminDashboardData["recent_logins"][number], index: number) => (
                <li key={index} className="flex items-center justify-between gap-3 py-3 first:pt-0">
                  <div className="min-w-0">
                    <p className="truncate font-medium text-slate-900">{item.user}</p>
                    <p className="truncate text-xs text-slate-500">{item.email}</p>
                  </div>
                  <span className="shrink-0 text-xs text-slate-400">{item.created_at}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Actividade Recente">
          {data.recent_activity.length === 0 ? (
            <EmptyState title="Sem actividade" description="Nenhuma acção registada." />
          ) : (
            <ul className="divide-y divide-slate-100">
              {data.recent_activity.map((item: AdminDashboardData["recent_activity"][number], index: number) => (
                <li key={index} className="py-3 first:pt-0">
                  <p className="font-medium text-slate-900">{item.action}</p>
                  <p className="text-sm text-slate-600">{item.description}</p>
                  <p className="mt-1 text-xs text-slate-400">
                    {item.user} · {item.created_at}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Actividade — Pacientes">
          {(data.recent_patient_activity ?? []).length === 0 ? (
            <EmptyState title="Sem actividade" description="Nenhuma acção em pacientes." />
          ) : (
            <ul className="divide-y divide-slate-100">
              {(data.recent_patient_activity ?? []).map((item, index) => (
                <li key={index} className="py-3 first:pt-0">
                  <p className="font-medium text-slate-900">{item.action}</p>
                  <p className="text-sm text-slate-600">{item.description}</p>
                  <p className="mt-1 text-xs text-slate-400">
                    {item.user} · {item.created_at}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
