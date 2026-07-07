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

import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { ROLE_LABELS } from "@/constants/roles";
import { dashboardService } from "@/services/dashboard";
import type { AdminDashboardData } from "@/types/user-management";

export function AdminDashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: dashboardService.getAdminSummary,
  });

  if (isLoading || !data) {
    return <Spinner label="A carregar dashboard..." />;
  }

  const cards = [
    { label: "Total de Utilizadores", value: data.cards.total_users },
    { label: "Utilizadores Ativos", value: data.cards.active_users },
    { label: "Utilizadores Inativos", value: data.cards.inactive_users },
    { label: "Novos Utilizadores (7 dias)", value: data.cards.new_users_week },
    { label: "Sessões Ativas", value: data.cards.active_sessions },
    { label: "Total de Pacientes", value: data.cards.total_patients },
    { label: "Pacientes Ativos", value: data.cards.active_patients },
    { label: "Pacientes Inativos", value: data.cards.inactive_patients },
    { label: "Novos Pacientes (7 dias)", value: data.cards.new_patients_week },
  ];

  const roleChartData = data.users_by_role.map((item: { role: string; count: number }) => ({
    name: ROLE_LABELS[item.role] ?? item.role,
    total: item.count,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Dashboard Administrativo</h2>
        <p className="mt-1 text-sm text-slate-500">Visão geral da gestão de utilizadores</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((card) => (
          <Card key={card.label} title={card.label}>
            <p className="text-3xl font-bold text-primary-700">{card.value}</p>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Utilizadores por Perfil">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={roleChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="total" fill="#2563eb" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card title="Logins (últimos 7 dias)">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.logins_by_day}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#0ea5e9" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Últimos Logins">
          <ul className="space-y-3 text-sm">
            {data.recent_logins.map((item: AdminDashboardData["recent_logins"][number], index: number) => (
              <li key={index} className="flex justify-between border-b border-slate-100 pb-2">
                <span>{item.user} ({item.email})</span>
                <span className="text-slate-500">{item.created_at}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Atividade Recente">
          <ul className="space-y-3 text-sm">
            {data.recent_activity.map((item: AdminDashboardData["recent_activity"][number], index: number) => (
              <li key={index} className="border-b border-slate-100 pb-2">
                <p className="font-medium text-slate-800">{item.action}</p>
                <p className="text-slate-600">{item.description}</p>
                <p className="text-xs text-slate-400">{item.user} — {item.created_at}</p>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Atividade Recente — Pacientes">
          <ul className="space-y-3 text-sm">
            {(data.recent_patient_activity ?? []).map((item, index) => (
              <li key={index} className="border-b border-slate-100 pb-2">
                <p className="font-medium text-slate-800">{item.action}</p>
                <p className="text-slate-600">{item.description}</p>
                <p className="text-xs text-slate-400">{item.user} — {item.created_at}</p>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  );
}
