import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { PageHeader } from "@/components/layout/PageHeader";
import { KpiCard } from "@/components/ui/KpiCard";
import { Badge, Card, ErrorState, SkeletonCard } from "@/design-system";
import { ROLE_LABELS } from "@/constants/roles";
import { dashboardService } from "@/services/dashboard";
import { settingsService } from "@/services/settings/settings.service";
import type { AdminDashboardData } from "@/types/user-management";

function statusLabel(ok: boolean | undefined) {
  if (ok === true) return { text: "Operacional", variant: "success" as const };
  if (ok === false) return { text: "Com falha", variant: "danger" as const };
  return { text: "Indisponível", variant: "warning" as const };
}

function readCheck(value: unknown): { ok?: boolean; status?: string } {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as { ok?: boolean; status?: string };
  }
  return {};
}

function formatBackupDate(value: unknown): string {
  if (typeof value === "string" && value) {
    try {
      return new Date(value).toLocaleString("pt-PT", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return value;
    }
  }
  return "Sem registos";
}

const ROLE_COLORS = ["#2563eb", "#0ea5e9", "#10b981", "#f59e0b", "#8b5cf6", "#64748b"];

const QUICK_LINKS = [
  { to: "/admin/users", label: "Utilizadores", desc: "Criar e gerir contas" },
  { to: "/admin/permissions", label: "Perfis e permissões", desc: "Controlo de acesso" },
  { to: "/settings/system", label: "Monitorização", desc: "Saúde do sistema" },
  { to: "/admin/audit", label: "Auditoria", desc: "Registo de acções" },
  { to: "/settings/backups", label: "Cópias de segurança", desc: "Restauro e arquivo" },
  { to: "/settings/feature-flags", label: "Funcionalidades", desc: "Activar módulos" },
];

export function AdminRoleDashboardPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: dashboardService.getAdminSummary,
    refetchInterval: 60_000,
  });

  const { data: system } = useQuery({
    queryKey: ["settings-system-dashboard"],
    queryFn: settingsService.getSystemDashboard,
    enabled: !isLoading,
  });

  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        message="Não foi possível carregar o painel de administração."
        onRetry={() => void refetch()}
      />
    );
  }

  const monitor = system?.monitorizacao ?? {};
  const database = readCheck(monitor.database);
  const redis = readCheck(monitor.redis);
  const celery = readCheck(monitor.celery);
  const health = typeof monitor.health === "string" ? monitor.health : "—";
  const version = typeof monitor.versao === "string" ? monitor.versao : "—";
  const ambiente = typeof monitor.ambiente === "string" ? monitor.ambiente : "—";

  const lastBackup = system?.backups_recentes?.[0];
  const lastBackupLabel = formatBackupDate(lastBackup?.created_at);
  const flagsActivas = (system?.feature_flags ?? []).filter((f) => f.activo).length;

  const roleChartData = data.users_by_role.map((item) => ({
    name: ROLE_LABELS[item.role] ?? item.role,
    total: item.count,
  }));

  const loginChartData = (data.logins_by_day ?? []).slice(-7).map((item) => ({
    name: item.date.slice(5),
    total: item.count,
  }));

  return (
    <div className="space-y-6">
      <PageHeader
        variant="hero"
        eyebrow="Administração do sistema"
        title="Painel do Administrador"
        description="Utilizadores, sessões, monitorização e segurança da plataforma SauVida."
        actions={
          <Link
            to="/admin/users"
            className="inline-flex h-11 items-center rounded-xl bg-primary-600 px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-700"
          >
            Gerir utilizadores
          </Link>
        }
      />

      {/* System health strip */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Base de dados", check: database },
          { label: "Cache", check: redis },
          { label: "Tarefas em fundo", check: celery },
          {
            label: "Estado geral",
            check: { ok: health === "ok", status: health === "ok" ? "saudável" : health },
          },
        ].map((item) => {
          const badge = statusLabel(item.check.ok);
          return (
            <div
              key={item.label}
              className="flex items-center justify-between rounded-2xl border border-slate-200/80 bg-white px-4 py-3 shadow-sm"
            >
              <div>
                <p className="text-xs font-medium tracking-wide text-slate-500 uppercase">{item.label}</p>
                <p className="mt-1 text-sm font-semibold text-slate-900 capitalize">
                  {item.check.status ?? badge.text}
                </p>
              </div>
              <Badge variant={badge.variant}>{badge.text}</Badge>
            </div>
          );
        })}
      </div>

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          label="Utilizadores"
          value={data.cards.total_users}
          badge={{ text: `${data.cards.active_users} activos`, variant: "success" }}
          trend={`${data.cards.new_users_week} novos esta semana`}
        />
        <KpiCard
          label="Sessões em linha"
          value={data.cards.active_sessions}
          badge={{ text: "Agora", variant: "info" }}
        />
        <KpiCard
          label="Pacientes"
          value={data.cards.total_patients}
          badge={{ text: `+${data.cards.new_patients_week} esta semana`, variant: "success" }}
        />
        <KpiCard
          label="Cópias de segurança"
          value={system?.backups_recentes?.length ?? 0}
          badge={{ text: "Recentes", variant: "default" }}
          trend={`Última: ${lastBackupLabel}`}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        {/* Login trend */}
        <Card title="Acessos (7 dias)" className="lg:col-span-3">
          {loginChartData.length === 0 ? (
            <p className="py-10 text-center text-sm text-slate-500">Sem dados de acesso recentes.</p>
          ) : (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={loginChartData} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      borderRadius: 12,
                      border: "1px solid #e2e8f0",
                      boxShadow: "0 4px 12px rgb(15 23 42 / 0.08)",
                    }}
                  />
                  <Bar dataKey="total" name="Acessos" fill="#2563eb" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>

        {/* Roles */}
        <Card title="Utilizadores por perfil" className="lg:col-span-2">
          {roleChartData.length === 0 ? (
            <p className="py-10 text-center text-sm text-slate-500">Sem perfis registados.</p>
          ) : (
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={roleChartData} layout="vertical" margin={{ top: 4, right: 12, left: 8, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                  <XAxis type="number" allowDecimals={false} hide />
                  <YAxis
                    type="category"
                    dataKey="name"
                    width={96}
                    tick={{ fontSize: 11, fill: "#64748b" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      borderRadius: 12,
                      border: "1px solid #e2e8f0",
                    }}
                  />
                  <Bar dataKey="total" name="Contas" radius={[0, 6, 6, 0]}>
                    {roleChartData.map((_, index) => (
                      <Cell key={index} fill={ROLE_COLORS[index % ROLE_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card title="Acesso rápido" className="lg:col-span-3">
          <div className="grid gap-3 sm:grid-cols-2">
            {QUICK_LINKS.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="group rounded-xl border border-slate-200/80 bg-slate-50/50 px-4 py-3 transition hover:border-primary-200 hover:bg-primary-50/60"
              >
                <p className="text-sm font-semibold text-slate-900 group-hover:text-primary-700">{link.label}</p>
                <p className="mt-0.5 text-xs text-slate-500">{link.desc}</p>
              </Link>
            ))}
          </div>
        </Card>

        <Card title="Plataforma" className="lg:col-span-2">
          <dl className="space-y-3 text-sm">
            <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <dt className="text-slate-500">Versão</dt>
              <dd className="font-semibold text-slate-900">{version}</dd>
            </div>
            <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <dt className="text-slate-500">Ambiente</dt>
              <dd className="font-semibold capitalize text-slate-900">{ambiente}</dd>
            </div>
            <div className="flex items-center justify-between gap-3 border-b border-slate-100 pb-3">
              <dt className="text-slate-500">Funcionalidades activas</dt>
              <dd className="font-semibold text-slate-900">{flagsActivas}</dd>
            </div>
            <div className="flex items-center justify-between gap-3">
              <dt className="text-slate-500">Contas inactivas</dt>
              <dd className="font-semibold text-slate-900">{data.cards.inactive_users}</dd>
            </div>
          </dl>
        </Card>
      </div>

      <Card title="Últimos acessos">
        {data.recent_logins.length === 0 ? (
          <p className="py-6 text-center text-sm text-slate-500">Sem acessos recentes.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left text-xs font-semibold tracking-wide text-slate-500 uppercase">
                  <th className="pb-3 pr-4">Utilizador</th>
                  <th className="pb-3 pr-4">E-mail</th>
                  <th className="pb-3 pr-4">Endereço IP</th>
                  <th className="pb-3 text-right">Data</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_logins.slice(0, 8).map((item: AdminDashboardData["recent_logins"][number], index) => (
                  <tr key={index} className="border-b border-slate-50 last:border-0">
                    <td className="py-3 pr-4 font-medium text-slate-900">{item.user}</td>
                    <td className="py-3 pr-4 text-slate-500">{item.email || "—"}</td>
                    <td className="py-3 pr-4 text-slate-500">{item.ip_address || "—"}</td>
                    <td className="py-3 text-right text-slate-500">{item.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
