import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
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

import { IconCalendar, IconLab, IconPatients } from "@/components/icons";
import { KpiCard } from "@/components/ui/KpiCard";
import { Button, Card, EmptyState, LoadingState, SkeletonCard } from "@/design-system";
import { useAuth } from "@/contexts/AuthContext";
import { usePermissions } from "@/hooks/usePermissions";
import { dashboardService } from "@/services/dashboard";

const diasSemana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

function buildWeeklyTrend(activityDates: string[]) {
  const counts = Array(7).fill(0) as number[];
  const today = new Date();
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    const key = d.toISOString().slice(0, 10);
    counts[6 - i] = activityDates.filter((a) => a.startsWith(key)).length;
  }
  return counts.map((count, i) => {
    const d = new Date(today);
    d.setDate(today.getDate() - (6 - i));
    const isWeekend = d.getDay() === 0 || d.getDay() === 6;
    return {
      name: diasSemana[d.getDay()],
      total: count,
      fill: isWeekend ? "#10b981" : "#2563eb",
    };
  });
}

export function DashboardPage() {
  const { user } = useAuth();
  const { hasPermission } = usePermissions();

  const { data, isLoading } = useQuery({
    queryKey: ["clinical-dashboard"],
    queryFn: dashboardService.getClinicalSummary,
    enabled: hasPermission("patients.view"),
  });

  const { data: receptionData, isLoading: receptionLoading } = useQuery({
    queryKey: ["reception-dashboard"],
    queryFn: dashboardService.getReceptionSummary,
    enabled: hasPermission("reception.view"),
  });

  const chartData = useMemo(
    () =>
      data
        ? buildWeeklyTrend(data.recent_patient_activity.map((a) => a.created_at))
        : [],
    [data],
  );

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Painel Administrativo
          </h1>
          <p className="mt-1 text-slate-500">
            Bem-vindo, <span className="font-medium text-slate-700">{user?.full_name}</span>. Visão
            geral da clínica SauVida.
          </p>
        </div>
        {hasPermission("appointments.create") && (
          <Link to="/appointments">
            <Button size="lg">+ Nova Consulta</Button>
          </Link>
        )}
      </div>

      {hasPermission("patients.view") ? (
        isLoading || !data ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <KpiCard
                label="Total de Pacientes"
                value={data.cards.total_patients.toLocaleString("pt-PT")}
                badge={{ text: `+${data.cards.new_patients_week} esta semana`, variant: "success" }}
                icon={<IconPatients />}
              />
              <KpiCard
                label="Pacientes Ativos"
                value={data.cards.active_patients.toLocaleString("pt-PT")}
                badge={{ text: "Registos activos", variant: "info" }}
                icon={<IconCalendar />}
              />
              <KpiCard
                label="Pacientes Inativos"
                value={data.cards.inactive_patients.toLocaleString("pt-PT")}
                badge={
                  data.cards.inactive_patients > 0
                    ? { text: "Rever cadastro", variant: "warning" }
                    : { text: "Sem pendências", variant: "success" }
                }
                icon={<IconPatients />}
              />
              <KpiCard
                label="Novos (7 dias)"
                value={data.cards.new_patients_week}
                badge={{ text: "Última semana", variant: "default" }}
                icon={<IconLab />}
              />
            </div>

            <div className="grid gap-6 lg:grid-cols-5">
              <Card title="Tendência de Atendimentos" className="lg:col-span-3">
                <p className="-mt-2 mb-4 text-xs text-slate-500">Actividade de pacientes — últimos 7 dias</p>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} barSize={32}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#64748b" }} axisLine={false} tickLine={false} />
                      <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "#64748b" }} axisLine={false} tickLine={false} />
                      <Tooltip
                        contentStyle={{
                          borderRadius: "12px",
                          border: "1px solid #e2e8f0",
                          boxShadow: "0 4px 12px rgb(15 23 42 / 0.08)",
                        }}
                      />
                      <Bar dataKey="total" radius={[8, 8, 0, 0]}>
                        {chartData.map((entry, index) => (
                          <Cell key={index} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Card>

              <Card title="Acesso Rápido" className="lg:col-span-2">
                <div className="flex flex-col gap-3">
                  <Link to="/patients">
                    <Button className="w-full" variant="primary">
                      Lista de Pacientes
                    </Button>
                  </Link>
                  {hasPermission("patients.create") && (
                    <Link to="/patients/new">
                      <Button className="w-full" variant="outline">
                        Novo Paciente
                      </Button>
                    </Link>
                  )}
                  {hasPermission("appointments.view") && (
                    <Link to="/appointments">
                      <Button className="w-full" variant="ghost">
                        Agenda de Consultas
                      </Button>
                    </Link>
                  )}
                </div>
              </Card>
            </div>

            <Card
              title="Últimos Pacientes Registados"
              footer={
                <div className="text-center">
                  <Link to="/patients" className="text-sm font-medium text-primary-600 hover:text-primary-700">
                    Ver todos os pacientes →
                  </Link>
                </div>
              }
            >
              {data.recent_patients.length === 0 ? (
                <EmptyState title="Sem registos recentes" description="Os novos pacientes aparecerão aqui." />
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-100 text-left text-xs font-semibold tracking-wide text-slate-500 uppercase">
                        <th className="pb-3 pr-4">Paciente</th>
                        <th className="pb-3 pr-4">N.º Processo</th>
                        <th className="pb-3 text-right">Data</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.recent_patients.map((patient) => (
                        <tr
                          key={patient.id}
                          className="border-b border-slate-50 transition hover:bg-slate-50/80"
                        >
                          <td className="py-3 pr-4">
                            <Link
                              to={`/patients/${patient.id}`}
                              className="font-medium text-slate-900 hover:text-primary-600"
                            >
                              {patient.full_name}
                            </Link>
                          </td>
                          <td className="py-3 pr-4 text-slate-500">{patient.patient_number}</td>
                          <td className="py-3 text-right text-slate-500">{patient.created_at}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>

            <Card title="Actividade Recente — Pacientes">
              {data.recent_patient_activity.length === 0 ? (
                <EmptyState title="Sem actividade" description="Nenhuma acção registada recentemente." />
              ) : (
                <ul className="divide-y divide-slate-100">
                  {data.recent_patient_activity.map((item, index) => (
                    <li key={index} className="flex flex-col gap-1 py-4 first:pt-0 last:pb-0 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <p className="font-medium text-slate-900">{item.action}</p>
                        <p className="text-sm text-slate-600">{item.description}</p>
                      </div>
                      <p className="shrink-0 text-xs text-slate-400">
                        {item.user} · {item.created_at}
                      </p>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </>
        )
      ) : (
        <Card title="Módulos Disponíveis">
          <p className="text-sm text-slate-600">
            O seu perfil não inclui acesso ao módulo de Pacientes. A gestão de utilizadores está
            disponível em{" "}
            <Link to="/admin/dashboard" className="font-medium text-primary-600 hover:underline">
              Administração
            </Link>
            .
          </p>
        </Card>
      )}

      {hasPermission("reception.view") &&
        (receptionLoading || !receptionData ? (
          <LoadingState message="A carregar indicadores de receção..." />
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">Receção</h2>
              <Link to="/reception" className="text-sm font-medium text-primary-600 hover:underline">
                Ver painel completo →
              </Link>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <KpiCard
                label="Em Espera"
                value={receptionData.cards.patients_waiting}
                badge={{ text: "Agora", variant: "warning" }}
              />
              <KpiCard
                label="Tempo Médio"
                value={`${receptionData.cards.average_wait_minutes} min`}
                badge={{ text: "Espera", variant: "info" }}
              />
              <KpiCard
                label="Atendidos Hoje"
                value={receptionData.cards.attended_today}
                badge={{ text: "Hoje", variant: "success" }}
              />
              <KpiCard
                label="Emergências"
                value={receptionData.cards.active_emergencies}
                badge={
                  receptionData.cards.active_emergencies > 0
                    ? { text: "Crítico", variant: "danger" }
                    : { text: "Estável", variant: "success" }
                }
              />
            </div>
          </div>
        ))}
    </div>
  );
}
