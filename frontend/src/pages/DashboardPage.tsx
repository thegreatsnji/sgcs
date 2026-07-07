import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { Card, LoadingState } from "@/design-system";
import { useAuth } from "@/contexts/AuthContext";
import { usePermissions } from "@/hooks/usePermissions";
import { dashboardService } from "@/services/dashboard";

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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Painel principal</h2>
        <p className="mt-1 text-slate-600">
          Bem-vindo, {user?.full_name}. Visão geral da clínica SauVida.
        </p>
      </div>

      {hasPermission("patients.view") ? (
        isLoading || !data ? (
          <LoadingState message="A carregar indicadores clínicos..." />
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[
                { label: "Total de Pacientes", value: data.cards.total_patients },
                { label: "Pacientes Ativos", value: data.cards.active_patients },
                { label: "Pacientes Inativos", value: data.cards.inactive_patients },
                { label: "Novos (7 dias)", value: data.cards.new_patients_week },
              ].map((card) => (
                <Card key={card.label} title={card.label}>
                  <p className="text-3xl font-bold text-primary-700">{card.value}</p>
                </Card>
              ))}
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <Card title="Acesso rápido">
                <div className="flex flex-wrap gap-3">
                  <Link
                    to="/patients"
                    className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
                  >
                    Lista de Pacientes
                  </Link>
                  {hasPermission("patients.create") && (
                    <Link
                      to="/patients/new"
                      className="rounded-lg border border-primary-600 px-4 py-2 text-sm font-medium text-primary-700 hover:bg-primary-50"
                    >
                      Novo Paciente
                    </Link>
                  )}
                </div>
              </Card>

              <Card title="Últimos pacientes registados">
                <ul className="space-y-3 text-sm">
                  {data.recent_patients.length === 0 ? (
                    <li className="text-slate-500">Sem registos recentes.</li>
                  ) : (
                    data.recent_patients.map((patient) => (
                      <li key={patient.id} className="flex justify-between border-b border-slate-100 pb-2">
                        <Link to={`/patients/${patient.id}`} className="font-medium text-primary-700 hover:underline">
                          {patient.full_name} ({patient.patient_number})
                        </Link>
                        <span className="text-slate-500">{patient.created_at}</span>
                      </li>
                    ))
                  )}
                </ul>
              </Card>
            </div>

            <Card title="Atividade recente — Pacientes">
              <ul className="space-y-3 text-sm">
                {data.recent_patient_activity.length === 0 ? (
                  <li className="text-slate-500">Sem atividade registada.</li>
                ) : (
                  data.recent_patient_activity.map((item, index) => (
                    <li key={index} className="border-b border-slate-100 pb-2">
                      <p className="font-medium text-slate-800">{item.action}</p>
                      <p className="text-slate-600">{item.description}</p>
                      <p className="text-xs text-slate-400">
                        {item.user} — {item.created_at}
                      </p>
                    </li>
                  ))
                )}
              </ul>
            </Card>
          </>
        )
      ) : (
        <Card title="Módulos disponíveis">
          <p className="text-sm text-slate-600">
            O seu perfil não inclui acesso ao módulo de Pacientes. A gestão de utilizadores está
            disponível em{" "}
            <Link to="/admin/dashboard" className="font-medium text-primary-700 hover:underline">
              Administração
            </Link>
            .
          </p>
        </Card>
      )}

      {hasPermission("reception.view") && (
        receptionLoading || !receptionData ? (
          <LoadingState message="A carregar indicadores de receção..." />
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">Receção</h3>
              <Link to="/reception" className="text-sm font-medium text-primary-700 hover:underline">
                Ver painel completo
              </Link>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[
                { label: "Em espera", value: receptionData.cards.patients_waiting },
                { label: "Tempo médio", value: `${receptionData.cards.average_wait_minutes} min` },
                { label: "Atendidos hoje", value: receptionData.cards.attended_today },
                { label: "Emergências", value: receptionData.cards.active_emergencies },
              ].map((card) => (
                <Card key={card.label} title={card.label}>
                  <p className="text-3xl font-bold text-primary-700">{card.value}</p>
                </Card>
              ))}
            </div>
          </div>
        )
      )}
    </div>
  );
}
